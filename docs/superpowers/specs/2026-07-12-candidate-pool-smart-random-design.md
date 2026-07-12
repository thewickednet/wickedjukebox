# Candidate-pool optimization for `smart_prefetch` (toggleable) — design

**Date:** 2026-07-12
**Status:** Approved (design)
**Repo:** `wickedjukebox` (player daemon)

## Problem

The `smart_prefetch` autoplay picker (`core/smartfind.py::find_song`) scores songs
in SQL and does `ORDER BY <score containing RAND()> LIMIT 10`. When no selective
filter bounds the scan, this is a **full-table temp-table + filesort over the whole
`song` library on every pick** — O(N) in library size, index-immune.

Measured on the **production dump (73,057 songs) on the real jukebox hardware**
(Ryzen 7 6800U, 8 GiB InnoDB buffer pool), via `sandbox/bench_pick.py`:

| scenario | median | worst |
|---|---|---|
| smart pick, **mood window off** (`fiction`/`sdf`/`dummy`) | **~460–680 ms** | ~835 ms |
| smart pick, `wicked` mood 0–15 (narrow window) | ~35 ms | 42 ms |
| candidate-pool prototype, K=300 | **~17 ms** | 23 ms |
| candidate-pool prototype, K=800 | ~42 ms | 60 ms |

Findings:
- The cost is **compute-bound** (the buffer pool is a healthy 8 GiB; cold-vs-warm
  gap is small), so tuning the DB won't help — only *not scanning the whole table*.
- A **narrow mood window is already fast** because the `song_mood_score_idx` index
  bounds the scored set. The slow path is specifically **mood-off** picks.
- A random candidate pool cuts the mood-off pick ~**27×** (to ~17 ms at K=300) and
  keeps it **flat** as the library grows.

## Goal / non-goals

**Goal:** bound the scored candidate set with a random-id pool *when nothing else
bounds it*, cutting the mood-off pick from O(N) to O(K). Ship it behind a
**per-channel config toggle that defaults to today's exact behavior**, so it can be
enabled/tuned/rolled back per channel with no redeploy.

**Explicit non-goals:**
- Not a gap/latency fix — even the ~0.8 s worst case is ~6× under the 5 s prefetch
  threshold, so there is no silence risk. This is DB-load / scalability hygiene.
- Not changing scoring semantics beyond "best of a random sample" (see below).
- Not touching the quick `Song.random` startup path (runs once per channel start;
  negligible cost).
- Not fixing the `DynamicPlaylist.apply_to` per-pick exception (tracked separately).
- Not addressing a *wide* (non-selective) mood window — see Limitations.

## Design

### The toggle: `candidate_pool_size`

A new per-channel config value on the `smart_prefetch` autoplay component:

```ini
[channel:example:autoplay]
type = smart_prefetch
; Bound the "smart random" scan to a random pool of this many candidate songs.
; 0 (or omitted) = disabled -> the original full-table scoring (unchanged).
; A few hundred is plenty; ~17 ms at 300, ~42 ms at 800 on the prod box.
candidate_pool_size = 500
```

- `0` or **absent** → **current full-scan behavior, byte-for-byte unchanged.**
- `> 0` → pooled fast-path drawing that many random candidate ids.

**Config read — approach (b), zero migration.** The key is read *optionally*, so
existing deployments keep working untouched (absent = 0 = off):

- Add `ConfigKeys.CANDIDATE_POOL_SIZE = ConfigOption(ConfigScope.CHANNEL, "autoplay", "candidate_pool_size")` (`config.py`).
- In `SmartPrefetch.configure()` (`component/random.py`), read it via the config
  abstraction with a fallback:
  ```python
  pool_size = self._config.get(
      ConfigKeys.CANDIDATE_POOL_SIZE, fallback=0,
      channel=self.channel_name, converter=int,
  )
  ```
- **Do NOT** add `candidate_pool_size` to `SmartPrefetch.CONFIG_KEYS`. `Config.dictify`
  (`config.py:147`) requires *every* declared `CONFIG_KEYS` entry to be present in the
  section and raises `ConfigError` otherwise; keeping the key out of `CONFIG_KEYS`
  means no existing config needs editing.
- Store it in the scoring config: `scoring_config[ScoringConfig.CANDIDATE_POOL_SIZE] = pool_size`.

Add `ScoringConfig.CANDIDATE_POOL_SIZE = "candidate_pool_size"` (`core/smartfind.py`).

### The pooled fast-path in `find_song`

The rule that avoids the narrow-mood correctness trap:

> **Apply the pool only on picks where the channel has no active mood window.**
> When a mood window is active, the `song_mood_score_idx` index already bounds the
> scan (measured fast), so pooling would add nothing and could double-query on a
> pool-miss. The pool is the bound *when nothing else is bounding the scan.*

`mood_range` is already read fresh per pick (`Channel.mood_range`, honoring live
web-UI changes). So the per-pick decision is:

```
pool_size = scoring_config[ScoringConfig.CANDIDATE_POOL_SIZE]   # 0 if disabled
mood_range = Channel.mood_range(session, channel_name) if channel_name else None

if pool_size > 0 and mood_range is None:
    # --- pooled fast-path (mood off; pool bounds the scan) ---
    pool = draw_pool(session, pool_size)          # random ids in [MIN(id), MAX(id)]
    candidate = <base scoring query>.filter(Song.id.in_(pool)).limit(10).first()
    if candidate is not None:
        return <finalize candidate>               # reuse existing finalize block
    # pool came up empty (pathological: tiny pool + heavy filters) -> fall through

# --- unchanged current behavior ---
# (mood path with its existing mood -> unfiltered "never silent" fallback,
#  OR the full-table scan when pooling is disabled / fell through)
```

- The `<base scoring query>` is exactly what `find_song` builds today (the
  `smart_random_no_users` / `smart_random_with_users` builder chosen by the active-user
  count, plus the `broken` / `exclude_from_random` filters and `DynamicPlaylist.apply_to`).
  The only addition is `.filter(Song.id.in_(pool))`.
- **`draw_pool(session, n)`**: `SELECT MIN(id), MAX(id) FROM song` (two indexed
  lookups, effectively free), then `n` distinct random integers in `[min, max]`
  (Python `random`; dedupe with a set). Id gaps and the `broken`/`duration` filters
  trim it slightly — `n` is the number of *ids drawn*, not guaranteed survivors, which
  is fine (a few hundred survivors is ample). No separate oversample knob.

### Fallback / never-go-silent contract (preserved)

- **mood off + pool > 0:** pooled pick. On the (pathological) empty pool, fall through
  to the current full-table pick → never silent.
- **mood on:** current mood path unchanged, including its existing mood→unfiltered
  fallback. Pool is not applied, so a narrow window can never be "missed" by sampling.
- **pool = 0:** current behavior on every pick.

So the change is **never silent and never worse than today**, and mood correctness is
untouched.

### Scoring semantics

With pooling, a mood-off pick is "best-scored of a random ~K sample" rather than
"global best-scored (with a RAND() term)." This is aligned with the picker's existing
`weight_randomness` (it is deliberately non-deterministic). One documented nuance:
global *never-played* prioritization becomes slightly softer (a random sample surfaces
never-played songs in proportion rather than surfacing all of them at once). Acceptable
for a jukebox; opt-in via the toggle regardless.

## Files touched

- `wickedjukebox/core/smartfind.py` — `ScoringConfig.CANDIDATE_POOL_SIZE`;
  `draw_pool()` helper; the pooled fast-path + fall-through in `find_song`; extract the
  candidate-finalize block into a small helper so both paths share it.
- `wickedjukebox/component/random.py` — `SmartPrefetch.configure()` reads
  `candidate_pool_size` (approach b) into `scoring_config`; document the key in the
  `SmartPrefetch` docstring.
- `wickedjukebox/config.py` — `ConfigKeys.CANDIDATE_POOL_SIZE`.
- `config.ini.dist` — document `candidate_pool_size` (default 0).

`SmartPrefetchThread.run` needs no change (it already passes `scoring_config` to
`find_song`).

## Testing

- **Regression:** `candidate_pool_size` absent / 0 → `find_song` behaves exactly as
  today (existing `test_prefetcher.py` tests stay green).
- **Pooled pick:** with `pool_size > 0` and mood off, `find_song` returns a song and
  only considers pooled ids (verifiable by seeding a small DB and asserting the pick is
  in the drawn pool, or by asserting the query carries an `id IN (...)` clause).
- **Never silent:** pool that matches nothing → still returns a song (falls through).
- **Mood on ignores pool:** with a mood window active, the pool is not applied
  (the pick honors the mood window; the narrow-window case is not "missed").
- **Config (approach b):** a `smart_prefetch` section *without* `candidate_pool_size`
  configures cleanly (no `ConfigError`) and yields pool_size 0.

## Verification / success criteria

- Full daemon `pytest` green (existing + new).
- `candidate_pool_size=0` path is behavior-identical to today.
- With the toggle on, `sandbox/bench_pick.py` on the jukebox shows the mood-off pick
  drop from ~0.5 s to tens of ms (end-to-end confirmation on real hardware).

## Recommended default

`candidate_pool_size ≈ 300–500` — on the prod box that is ~17–30 ms per pick with
ample scoring diversity. Keep it modest on the 6800U (K=800 ≈ 42 ms is fine but
unnecessary).

## Limitations (documented, out of scope)

- A **wide, non-selective mood window** (e.g. 0–100) is treated as "mood on" and is
  *not* pooled, so it stays a full scan. Mood windows are meant to narrow the set; the
  fix is to use a narrow window or turn mood off (then pooling applies). Not handled
  here.
- The pooled query uses a large `id IN (...)` list; on very weak hardware a big K
  costs more (measured: K=800 ≈ 42 ms on prod). Mitigated by the modest recommended K.
- `Song.random` (quick startup pick) still does `ORDER BY RAND()`; unchanged (runs once
  per channel start).
- `DynamicPlaylist.apply_to` still throws + logs on every pick (pre-existing, separate).
- The pool samples uniformly over `[MIN(id), MAX(id)]`, so it assumes **reasonably
  dense** song ids. If ids are very sparse or a single outlier inflates `MAX(id)`,
  most drawn ids miss real rows → the pool matches nothing → it correctly falls
  through to the full scan (no crash, just no speedup). Auto-increment ids are
  normally dense, so this is fine in practice.
