# Fix the `smart_prefetch` scoring terms (recency + never-played), drop song-age — design

**Date:** 2026-07-12
**Status:** Approved (design)
**Repo:** `wickedjukebox` (player daemon)

## Problem

The `smart_prefetch` picker scores songs via `core/smartfind.py::score_expression`
and `model/db/stats.py::ChannelStat.last_played_parametric`. Several bugs make the
scoring terms produce garbage, so the "smart" picker is effectively dominated by its
random term today. (This is **only** `smart_prefetch`; `AllFilesRandom` has no
scoring and is unaffected. The user love/hate rating in `smart_random_with_users`
is correct and untouched by this change.)

**Bugs:**
1. `smartfind.py` — `func.if_(ChannelStat.lastPlayed is None, never_played, 0)`:
   `lastPlayed is None` is a Python identity check on a Column → always `False` →
   the never-played bonus is **dead (always 0)**. Must be `.is_(None)` (SQL `IS NULL`).
2. `stats.py` — `last_played_parametric.expression` ends `… / lp_cutoff * cls.lastPlayed`:
   multiplies by the `lastPlayed` **datetime column** instead of `weight` (the Python
   hybrid correctly uses `* weight`). The recency term is nonsense.
3. Units — `func.now() - cls.lastPlayed` and `func.now() - Song.added`: in MySQL,
   `DATETIME - DATETIME` is a `YYYYMMDDHHMMSS` numeric subtraction, **not seconds**,
   yet the cutoffs are in seconds. Must use `UNIX_TIMESTAMP(...)` differences.
4. `stats.py` — the Python hybrid does `.total_seconds` (a method, not called) →
   `TypeError` if invoked on an instance.
5. Direction — even fixed literally, the recency term rewards recently-played songs,
   the opposite of the documented intent ("negatively impacts songs played very
   recently").

## Decision (user-approved)

Fix the terms to **match the documented intent**, and **remove the song-age term
entirely** (the user decided "long in the DB" should not influence scoring).

### Corrected `score_expression`

```
score = − recency_penalty            [weight_last_played]
        + never_played_bonus          [weight_never_played]
        + randomness                  [weight_randomness]
```

- **Recency penalty** = `(1 − LEAST(secs_since_played, LAST_PLAYED_CUTOFF)/LAST_PLAYED_CUTOFF) × weight_last_played`
  → full penalty right after playing, decaying linearly to 0 by `LAST_PLAYED_CUTOFF`
  (7 days). `secs_since_played` = `UNIX_TIMESTAMP(now()) − UNIX_TIMESTAMP(lastPlayed)`.
  **Never-played** (`lastPlayed IS NULL`) → the expression yields NULL → the caller's
  `func.ifnull(..., 0)` maps it to **0 penalty**.
- **Never-played bonus** = `+ weight_never_played` when `lastPlayed IS NULL`
  (`func.if_(ChannelStat.lastPlayed.is_(None), never_played, 0)`).
- **Randomness** unchanged (`(func.rand() * randomness * 2) - randomness`).
- **Song age** — removed (no term).

Behavioral ordering (with defaults `last_played=10, never_played=4`): never-played
(~+4) > long-idle (~0) > recently-played (~−5) > just-played (~−10). The picker
finally favors never-played and long-idle songs and avoids recently-played ones.

### `ChannelStat.last_played_parametric` (both hybrid + expression)

- **Expression:** `(1 − func.least(age, lp_cutoff) / lp_cutoff) * weight` where
  `age = func.unix_timestamp(func.now()) - func.unix_timestamp(cls.lastPlayed)`.
  NULL-propagates for never-played (caller maps to 0).
- **Python hybrid:** return `0.0` when `lastPlayed is None`; else
  `(1 - min(age, lp_cutoff) / lp_cutoff) * weight` with
  `age = (datetime.now() - self.lastPlayed).total_seconds()` (parentheses fixed).
- The caller in `score_expression` changes its `func.ifnull(..., LAST_PLAYED_CUTOFF)`
  default to `func.ifnull(..., 0)` so never-played incurs **no** recency penalty.

## Plumbing cleanup (song-age removal)

Because song-age is dropped, remove its now-dead plumbing (all backwards-compatible —
`Config.dictify` ignores *extra* config keys, so an existing config still carrying
`weight_song_age` just has it ignored):

- `core/smartfind.py` — drop the `song_age` parameter from `score_expression`,
  `smart_random_no_users`, `smart_random_with_users`, and the `song_age` local +
  builder call args in `find_song`; delete the `SONG_AGE_CUTOFF` constant and its TODO.
- `core/smartfind.py` — remove `ScoringConfig.SONG_AGE`.
- `component/random.py` — remove `"weight_song_age"` from `SmartPrefetch.CONFIG_KEYS`,
  remove the `ScoringConfig.SONG_AGE: int(cfg["weight_song_age"])` line in `configure()`,
  and delete the `weight_song_age` block from the `SmartPrefetch` docstring.
- `config.ini.dist` — remove the `weight_song_age = 1` line + its comment.

## Files touched

- `wickedjukebox/model/db/stats.py` — `ChannelStat.last_played_parametric` (hybrid + expression).
- `wickedjukebox/core/smartfind.py` — `score_expression`, `smart_random_no_users`,
  `smart_random_with_users`, `find_song`, remove `SONG_AGE_CUTOFF` + `ScoringConfig.SONG_AGE`.
- `wickedjukebox/component/random.py` — `SmartPrefetch.CONFIG_KEYS`, `configure`, docstring.
- `config.ini.dist` — drop `weight_song_age`.
- `test/test_prefetcher.py` — update `SCORING_CONFIG` (drop `SONG_AGE`); new scoring tests.

The user love/hate rating (`smart_random_with_users`, `get_standing_query`) and all
filters (`max_duration`, mood window, `broken`, `exclude_from_random`, dynamic
playlist, candidate-pool) are **unchanged**.

## Testing

The scoring math is the deliverable, so test it directly and deterministically:

- **Formula tests (deterministic, `weight_randomness = 0`):** build the scoring query
  (`smart_random_no_users` with the corrected weights) or `score_expression` and read
  the `(id, score)` rows, so results don't depend on `RAND()` and aren't gated by
  `find_song`'s `if not candidate.score` guard. Seed songs + `channel_song_data`
  (`ChannelStat`) rows with controlled `lastPlayed` / never-played state and assert:
  - a **recently-played** song scores **below** a **long-idle** song (played ≥ cutoff ago),
  - a **never-played** song's score `== weight_never_played` and is **above** a
    long-idle *played* song (score ~0),
  - a **just-played** song's recency penalty ≈ `weight_last_played` below long-idle.
- **Integration test:** with a small nonzero `weight_randomness` and a large score gap
  (e.g. never-played vs just-played), assert `find_song` returns the clearly-winning
  song — confirming the end-to-end pick honors the corrected ordering.
- **Regression:** the existing prefetcher tests stay green after `SCORING_CONFIG` drops
  `SONG_AGE`.

## Non-goals

- Not expanding what `smart_prefetch` scores on (no new parameters).
- Not touching `AllFilesRandom`, the user love/hate rating logic, or any filter.
- Not fixing the pre-existing multi-channel double-count in the `channel_song_data`
  LEFT JOIN (the join isn't channel-scoped) — separate latent issue, out of scope.
- Not fixing the `DynamicPlaylist.apply_to` per-pick exception (separate).

## Risks

- **Behavioral change on the live jukebox:** picks will change (for the first time the
  scoring actually works). This is the intended outcome; it's opt-in only in that it
  affects channels using `type = smart_prefetch`.
- **NULL propagation** in the recency expression must yield 0 penalty for never-played
  — covered by a formula test.
- **`find_song`'s `if not candidate.score` guard** returns None on an exactly-0.0 score;
  formula tests read the score column directly to avoid it, and the integration test
  uses a nonzero randomness so the winner's score is nonzero.
