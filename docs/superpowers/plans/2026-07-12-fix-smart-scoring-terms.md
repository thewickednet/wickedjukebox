# Fix `smart_prefetch` scoring terms (recency + never-played), drop song-age — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the broken recency and never-played scoring terms so `smart_prefetch` actually de-prioritizes recently-played songs and favors never-played ones, and remove the song-age term entirely.

**Architecture:** Rewrite `ChannelStat.last_played_parametric` (recency penalty in seconds) and `score_expression` (recency + never-played, no age); drop the `song_age` parameter and its config/enum/doc plumbing. Behavior-only change to `smart_prefetch`; `AllFilesRandom`, the user love/hate rating, and all filters are untouched.

**Tech Stack:** Python 3.10, SQLAlchemy < 2.0, MariaDB, pytest.

## Global Constraints

- **SQLAlchemy pinned `< 2.0`.**
- **Scope:** `smart_prefetch` scoring only. Do NOT touch `AllFilesRandom`, `get_standing_query` / the user love-hate rating in `smart_random_with_users`, the candidate-pool logic, or any filter (`max_duration`, mood, `broken`, `exclude_from_random`, dynamic playlist).
- **Song-age removal is backwards-compatible:** `Config.dictify` ignores *extra* config keys, so an existing config still carrying `weight_song_age` keeps working (the key is just ignored once removed from `CONFIG_KEYS`).
- **Never-played must incur no recency penalty:** the recency expression NULL-propagates for `lastPlayed IS NULL` and the caller maps it to `0`.
- Formatting: black + isort, **line-length 80**, pinned **black 23.3.0 / isort 5.12.0**.
- **Spec:** `docs/superpowers/specs/2026-07-12-fix-smart-scoring-terms-design.md`.

## Environment (already provisioned — verify, don't rebuild)

- Venv `~/.virtualenvs/wickedjukebox/bin/{python,pytest}`. Tests run against the config DSN (MariaDB container port 33066); `conftest.py` builds the schema + rolls back per test (fixtures `dbsession`, `default_data`; `default_data` has `default_song`, `default_channel` = "test-channel", `default_artist`, `default_album`, `default_user`).
- Baseline: run `~/.virtualenvs/wickedjukebox/bin/pytest -q 2>&1 | tail -1` first (should be 127 passing). Only the new scoring tests change the count.
- Pinned formatters `/tmp/wjfmt/bin/{black,isort}` (recreate if missing: `python -m venv /tmp/wjfmt && /tmp/wjfmt/bin/pip -q install black==23.3.0 isort==5.12.0`).

---

## Task 1: Fix the scoring terms and remove song-age

**Files:**
- Modify: `wickedjukebox/model/db/stats.py` (`ChannelStat.last_played_parametric`, both hybrid + expression)
- Modify: `wickedjukebox/core/smartfind.py` (`score_expression`, `smart_random_no_users`, `smart_random_with_users`, `find_song`, remove `SONG_AGE_CUTOFF` + `ScoringConfig.SONG_AGE`)
- Modify: `wickedjukebox/component/random.py` (`SmartPrefetch.CONFIG_KEYS`, `configure`, docstring)
- Modify: `config.ini.dist`
- Test: `test/test_prefetcher.py`

**Interfaces:**
- Changed signatures (drop `song_age`): `score_expression(last_played, never_played, randomness)`, `smart_random_no_users(session, never_played, last_played, randomness, max_random_duration)`, `smart_random_with_users(session, never_played, user_rating, last_played, proofoflife_timeout, randomness, max_random_duration, num_active_users)`.
- Removed: `ScoringConfig.SONG_AGE`, `SONG_AGE_CUTOFF`.
- `ChannelStat.last_played_parametric(lp_cutoff, weight)` now returns a **recency penalty** (≈`weight` right after playing, 0 by `lp_cutoff`, NULL/0 for never-played).

- [ ] **Step 1: Write the RED-driver test (via `find_song`, stable signature)**

Append to `test/test_prefetcher.py` (add imports at the top with the others):
```python
from datetime import datetime, timedelta

from wickedjukebox.model.db.stats import ChannelStat
```
Then add a helper and the test:
```python
def _mark_played(dbsession, default_data, song, when):
    stat = ChannelStat(
        song_id=song.id, channel_id=default_data["default_channel"].id
    )
    stat.lastPlayed = when
    dbsession.add(stat)
    dbsession.flush()
    return stat


def test_find_song_favors_never_played_over_recent(
    dbsession: Session, default_data: Dict[str, Any]
):
    """A never-played song must outrank a just-played one."""
    _mark_played(
        dbsession, default_data, default_data["default_song"], datetime.now()
    )
    never = _add_song(dbsession, default_data, "never.mp3", None)
    cfg = {
        ScoringConfig.USER_RATING: 4,
        ScoringConfig.LAST_PLAYED: 10,
        ScoringConfig.NEVER_PLAYED: 4,
        ScoringConfig.RANDOMNESS: 0,
        ScoringConfig.MAX_DURATION: 600,
        ScoringConfig.PROOF_OF_LIFE_TIMEOUT: 120,
    }
    song = find_song(dbsession, cfg, True)  # no channel -> mood off
    assert song is not None
    assert song.id == never.id
```

- [ ] **Step 2: Run it to verify it FAILS (RED)**

Run: `~/.virtualenvs/wickedjukebox/bin/pytest test/test_prefetcher.py::test_find_song_favors_never_played_over_recent -v`
Expected: FAIL. Today never-played gets `− LAST_PLAYED_CUTOFF` (the *worst* score, ~−604800) and the never-played bonus is dead, so `find_song` returns the just-played song, not `never`. (The `cfg` above omits `ScoringConfig.SONG_AGE`; if the current code raises `KeyError` on it that is also a valid RED — it's removed in Step 4.)

- [ ] **Step 3: Rewrite `ChannelStat.last_played_parametric`**

In `wickedjukebox/model/db/stats.py`, replace the whole `last_played_parametric` hybrid+expression block:
```python
    @hybrid_method
    def last_played_parametric(self, lp_cutoff, weight) -> float:
        if self.lastPlayed is None:
            return 1.0
        from datetime import datetime

        return (
            min(lp_cutoff, (datetime.now() - self.lastPlayed).total_seconds)
            / lp_cutoff
            * weight
        )

    @last_played_parametric.expression
    def last_played_parametric(cls, lp_cutoff, weight):
        from sqlalchemy import func

        return (
            func.ifnull(
                func.least(lp_cutoff, (func.now() - cls.lastPlayed)), lp_cutoff
            )
            / lp_cutoff
            * cls.lastPlayed
        )
```
with:
```python
    @hybrid_method
    def last_played_parametric(self, lp_cutoff, weight) -> float:
        """
        Recency penalty: ``weight`` right after playing, decaying linearly to 0
        by ``lp_cutoff`` seconds. Never-played (``lastPlayed`` is None) -> 0.
        """
        if self.lastPlayed is None:
            return 0.0
        from datetime import datetime

        age = (datetime.now() - self.lastPlayed).total_seconds()
        return (1 - min(age, lp_cutoff) / lp_cutoff) * weight

    @last_played_parametric.expression
    def last_played_parametric(cls, lp_cutoff, weight):
        from sqlalchemy import func

        # seconds since last play; NULL for never-played (caller maps to 0)
        age = func.unix_timestamp(func.now()) - func.unix_timestamp(
            cls.lastPlayed
        )
        return (1 - func.least(age, lp_cutoff) / lp_cutoff) * weight
```

- [ ] **Step 4: Rewrite `score_expression` (fix recency+never, drop age) and remove `SONG_AGE_CUTOFF` / `ScoringConfig.SONG_AGE`**

In `wickedjukebox/core/smartfind.py`:

(a) Delete the `SONG_AGE_CUTOFF` constant + its comment (currently lines 31-35):
```python
#: A song gains a boost related to its age in the DB. This value defines a
#: relative point in time when it received the maximum value. TODO: Whether this
#: is based on recency or primacy needs to be digested from the source-code and
#: clarified.
SONG_AGE_CUTOFF = 14 * 24 * 60 * 60
```
(delete those 5 lines, leaving `LAST_PLAYED_CUTOFF` above them intact).

(b) Remove the `SONG_AGE` enum member:
```python
    SONG_AGE = "song_age"
```
(delete that one line from `ScoringConfig`).

(c) Replace the whole `score_expression` function:
```python
def score_expression(
    last_played: int, never_played: int, song_age: int, randomness: float
):
    """
    Generates a column-expression that calculates the scoring for a song without
    taking into account user-statistics.
    """
    return (
        0
        - func.ifnull(
            ChannelStat.last_played_parametric(LAST_PLAYED_CUTOFF, last_played),
            LAST_PLAYED_CUTOFF,
        )
        + func.if_(ChannelStat.lastPlayed is None, never_played, 0)
        + func.ifnull(
            func.if_(
                (func.now() - Song.added) < SONG_AGE_CUTOFF,
                (func.now() - Song.added) / SONG_AGE_CUTOFF * song_age,
                0,
            ),
            0,
        )
        + ((func.rand() * randomness * 2) - randomness)
    )
```
with:
```python
def score_expression(last_played: int, never_played: int, randomness: float):
    """
    Column-expression scoring a song without user statistics:
      - recency penalty (recently-played scores lower; never-played: no penalty)
      - never-played bonus
      - randomness
    """
    return (
        0
        - func.ifnull(
            ChannelStat.last_played_parametric(LAST_PLAYED_CUTOFF, last_played),
            0,
        )
        + func.if_(ChannelStat.lastPlayed.is_(None), never_played, 0)
        + ((func.rand() * randomness * 2) - randomness)
    )
```

- [ ] **Step 5: Drop `song_age` from the two builders and `find_song`**

In `wickedjukebox/core/smartfind.py`:

(a) `smart_random_no_users` — remove the `song_age: int,` parameter (line ~117), delete the `:param song_age:` docstring paragraph (the 3 lines beginning `:param song_age:`), and change the `score_expression(...)` call from `score_expression(last_played, never_played, song_age, randomness)` to `score_expression(last_played, never_played, randomness)`.

(b) `smart_random_with_users` — remove the `song_age: int,` parameter (line ~160) and change the `score_expression(last_played, never_played, song_age, randomness)` call (the multi-line one) to drop `song_age`:
```python
    score = score_expression(
        last_played,
        never_played,
        song_age,
        randomness,
    ) + (func.ifnull(loves_query.c.count, 0) / num_active_users * user_rating)
```
becomes:
```python
    score = score_expression(
        last_played,
        never_played,
        randomness,
    ) + (func.ifnull(loves_query.c.count, 0) / num_active_users * user_rating)
```

(c) `find_song` — remove the coefficient line `song_age = scoring_config[ScoringConfig.SONG_AGE]` (line ~256), and remove the `song_age,` argument from both builder calls (the `smart_random_no_users(...)` call ~line 278 and the `smart_random_with_users(...)` call ~line 290).

- [ ] **Step 6: Remove the `weight_song_age` config plumbing**

In `wickedjukebox/component/random.py`:
- In the `SmartPrefetch` docstring, delete the two lines:
  ```
        ; Positively affects songs that have been long in the DB
        weight_song_age = 1
  ```
- In `CONFIG_KEYS`, delete the `"weight_song_age",` line.
- In `configure()`, delete the `ScoringConfig.SONG_AGE: int(cfg["weight_song_age"]),` line.

In `config.ini.dist`, delete the `weight_song_age = 1` line (line ~45).

- [ ] **Step 7: Update the test `SCORING_CONFIG`**

In `test/test_prefetcher.py`, remove `ScoringConfig.SONG_AGE: 4,` from the module-level `SCORING_CONFIG` dict.

- [ ] **Step 8: Run the RED-driver test → GREEN, then add precise score tests**

Run: `~/.virtualenvs/wickedjukebox/bin/pytest test/test_prefetcher.py::test_find_song_favors_never_played_over_recent -v`
Expected: PASS (never-played score +4 beats just-played −10).

Then append the deterministic score-column tests (new builder signature):
```python
def test_recency_and_never_played_scores(
    dbsession: Session, default_data: Dict[str, Any]
):
    """randomness=0 -> deterministic: recent < long-idle < never-played."""
    from wickedjukebox.core.smartfind import smart_random_no_users

    recent = default_data["default_song"]
    _mark_played(dbsession, default_data, recent, datetime.now())
    idle = _add_song(dbsession, default_data, "idle.mp3", None)
    _mark_played(
        dbsession, default_data, idle, datetime.now() - timedelta(days=8)
    )
    never = _add_song(dbsession, default_data, "never2.mp3", None)
    q = smart_random_no_users(
        dbsession,
        never_played=4,
        last_played=10,
        randomness=0,
        max_random_duration=600,
    )
    scores = {row.id: float(row.score) for row in q.all()}
    assert scores[recent.id] < scores[idle.id] < scores[never.id]
    assert abs(scores[idle.id]) < 1e-6  # played > cutoff ago: 0 penalty, no bonus
    assert abs(scores[never.id] - 4.0) < 1e-6  # never-played bonus
    assert scores[recent.id] < -9  # ~ -10 recency penalty


def test_song_added_does_not_affect_score(
    dbsession: Session, default_data: Dict[str, Any]
):
    """Song age no longer influences the score."""
    from wickedjukebox.core.smartfind import smart_random_no_users

    old = _add_song(dbsession, default_data, "old.mp3", None)
    new = _add_song(dbsession, default_data, "new.mp3", None)
    old.added = datetime.now() - timedelta(days=100)
    new.added = datetime.now()
    dbsession.flush()
    q = smart_random_no_users(
        dbsession,
        never_played=0,
        last_played=10,
        randomness=0,
        max_random_duration=600,
    )
    scores = {row.id: float(row.score) for row in q.all()}
    assert abs(scores[old.id] - scores[new.id]) < 1e-6
```

- [ ] **Step 9: Run the full suite**

Run: `~/.virtualenvs/wickedjukebox/bin/pytest -q 2>&1 | tail -3`
Expected: baseline (127) + 3 new = **130 passing, 0 failures**. If any pre-existing test referenced `ScoringConfig.SONG_AGE` or the old builder signature, update it (only `SCORING_CONFIG` should have; already handled in Step 7).

- [ ] **Step 10: Format and commit**

```bash
/tmp/wjfmt/bin/isort --profile black --line-length 80 wickedjukebox/model/db/stats.py wickedjukebox/core/smartfind.py wickedjukebox/component/random.py test/test_prefetcher.py
/tmp/wjfmt/bin/black --line-length 80 wickedjukebox/model/db/stats.py wickedjukebox/core/smartfind.py wickedjukebox/component/random.py test/test_prefetcher.py
git add wickedjukebox/model/db/stats.py wickedjukebox/core/smartfind.py wickedjukebox/component/random.py config.ini.dist test/test_prefetcher.py
git -c commit.gpgsign=false commit -m "fix(smartfind): repair recency + never-played scoring, drop song-age

last_played_parametric now returns a recency penalty in seconds (UNIX_TIMESTAMP,
xweight, never-played -> 0); score_expression penalizes recently-played and
bonuses never-played (.is_(None)); the song-age term and its weight_song_age /
ScoringConfig.SONG_AGE / SONG_AGE_CUTOFF plumbing are removed. User love/hate
rating and all filters unchanged.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review (completed by plan author)

**1. Spec coverage:** recency fix (Step 3-4) ✔; never-played `.is_(None)` + ifnull→0 (Step 4) ✔; song-age term + plumbing removal (Steps 4-7) ✔; `.total_seconds()` fix (Step 3) ✔; seconds via UNIX_TIMESTAMP (Step 3) ✔; deterministic formula tests + never-played integration test (Steps 1, 8) ✔; user-rating/filters untouched (Global Constraints) ✔.

**2. Placeholder scan:** none — every step shows exact before/after code and exact commands.

**3. Type/name consistency:** the dropped `song_age` parameter is removed consistently from `score_expression`, both builders, and both `find_song` call sites; `ScoringConfig.SONG_AGE` / `SONG_AGE_CUTOFF` / `weight_song_age` removed everywhere they appear (enum, builder params, config keys, configure, docstring, config.ini.dist, test SCORING_CONFIG). `last_played_parametric` returns a penalty consumed by `score_expression`'s `− func.ifnull(..., 0)`.

## Notes / risks

- The `find_song` `if not candidate.score` guard returns None on an exactly-0.0 top score; the deterministic score tests read the score column directly (via `smart_random_no_users`) to avoid it, and the RED-driver test uses a never-played winner whose score is clearly positive (+4).
- `smart_random_no_users` does not itself apply the broken/exclude/mood filters (those live in `find_song`), so the score-column tests see all seeded songs — intended.
- Behavioral change on the live jukebox is the point; it only affects `type = smart_prefetch` channels.
