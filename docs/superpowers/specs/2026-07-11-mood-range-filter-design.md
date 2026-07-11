# Mood range filter in the random pickers — design

**Date:** 2026-07-11
**Goal:** Honor the per-channel mood window (`channel.mood_low`/`mood_high`, written by the
djukebox web UI) when auto-picking random songs, in BOTH autoplay implementations
(`smart_prefetch` and `allfiles_random`). Contract source:
`djukebox/docs/integration-contract.md` §13 "Randomizer mood range (daemon contract)".

**Contract (binding):**
- Read the thresholds **fresh per pick** from the channel row (not startup-cached config).
- Filter: `mood_score IS NULL OR mood_score BETWEEN mood_low AND mood_high` — NULL (not yet
  analyzed) always passes.
- Empty filtered pool → fall back to an unfiltered pick; never go silent.
- `song.mood_score` (0–100, higher = more intense) is computed by djukebox; the daemon only
  reads it.

**User decision (2026-07-11):** filter in BOTH pickers — prod keeps `allfiles_random`; no
channel-config change is part of this feature.

## 1. ORM mapping + alembic parity migration

DB columns already exist in prod (Django migrations 0042/0043). The daemon needs:

- `Song.mood_score = Column(SmallInteger)` (`model/db/library.py`, after `crest_factor`
  block) — comment: computed by djukebox, NULL = not analyzed.
- `Channel.mood_low` / `Channel.mood_high = Column(SmallInteger)` (`model/db/playback.py`,
  after `owner_id`) — both NULL = filtering off.
- One alembic migration (new head after `c7a1e9b4f2d3`) adding the three columns + the
  `song_mood_score_idx` index, **unguarded plain `op.add_column`, exactly like the
  `b3d9f1a2c4e6_djukebox_field_parity` precedent**: the daemon's alembic chain only ever
  builds dev/test DBs; prod schema is Django-managed and already has the columns (the
  migration docstring says so). Include the symmetric `downgrade()`.

## 2. Threshold read — `Channel.mood_range`

New staticmethod on `Channel` (`model/db/playback.py`):

```python
@staticmethod
def mood_range(session, name):
    """Live mood window for *name*: (low, high) ints, or None = filtering off."""
    channel = Channel.by_name(session, name)
    if channel is None or channel.mood_low is None or channel.mood_high is None:
        return None
    return (channel.mood_low, channel.mood_high)
```

Called once per pick by every consumer — that is what makes threshold changes live. Both
pickers already carry `self.channel_name` (currently unused by the queries).

## 3. Smart picker (`core/smartfind.py` + `Song.random`)

- `find_song(session, scoring_config, is_mysql, channel_name=None)` — new optional param;
  `SmartPrefetchThread.run` passes `self.channel_name`. `None` ⇒ no mood filtering
  (existing tests unchanged).
- After the existing `broken`/`exclude_from_random`/`DynamicPlaylist` filters and before
  `limit`: resolve `mood_range`; when active add
  `or_(Song.mood_score.is_(None), Song.mood_score.between(low, high))`. Keep a handle on
  the pre-mood query; if the filtered `first()` is None and the filter was active, log and
  retry the unfiltered query (fallback contract).
- `Song.random(session, max_duration=None, mood_range=None)` (`model/db/library.py`) —
  same NULL-passes filter + same unfiltered fallback. The quick first prefetch in
  `SmartPrefetchThread.run` resolves the range via `Channel.mood_range` and passes it.
- **Accepted staleness (documented in the module docstring):** the prefetch queue holds at
  most one pick, so a threshold change can lag by ≤ 1 song on `smart_prefetch`.

## 4. Filesystem picker (`AllFilesRandom.pick`)

Stays filesystem-first; gains one DB session per pick (pattern: `with Session() as
session:` as used by `SmartPrefetchThread`):

- `samples = sample(candidates, min(MOOD_SAMPLE_SIZE, len(candidates)))` with
  `MOOD_SAMPLE_SIZE = 50` (module constant); default pick = `samples[0]` — when filtering
  is off this is behaviorally identical to today's `choice(candidates)`.
- When `Channel.mood_range` is active: iterate the samples; look up each row by
  `Song.by_filename(session, str(candidate.absolute()))` (the scanner writes
  `localpath` via `.absolute()`; the MPD return value stays `str(pick.resolve())` exactly
  as today). **No row or NULL `mood_score` passes**; in-range wins; all 50 out-of-range →
  log and keep `samples[0]` (unfiltered fallback).
- Rejection-sampling miss math: even with only 10 % of the library in range,
  P(all 50 miss) ≈ 0.5 %; the fallback then still plays something.
- No caching anywhere in this picker → threshold changes apply on the very next pick.

## 5. Tests (MariaDB suite, existing fixtures)

`test/test_prefetcher.py` additions (fixtures `dbsession` + `default_data`; the default
channel is `"test-channel"`):
- `find_song` with in-range / out-of-range / NULL `mood_score` × active window;
  `channel_name=None` and both-NULL window ⇒ no filtering; out-of-range only song ⇒
  fallback still returns it (never silent).
- `Song.random(mood_range=...)`: same matrix.
- `Channel.mood_range`: unknown channel, half-set window, full window.

New `test/test_allfiles_mood.py`: tmp_path mp3 files (empty files suffice — glob matches
names) + seeded Song rows with `localpath=str(p.absolute())`; patch
`wickedjukebox.component.random.Session` (context-manager returning `dbsession`, same
approach as `test_scanner.py` patches). Cases: filtering off ⇒ plain pick; in-range file
chosen over out-of-range; missing row passes; all-out-of-range ⇒ fallback returns
something; empty dir ⇒ `""` unchanged.

## 6. Out of scope

- No channel-config change (prod stays `allfiles_random`); no re-validation of the ≤1-song
  prefetch staleness at `SmartPrefetch.pick()` hand-off (YAGNI — accepted lag).
- No writing of `mood_score`/`mood_low`/`mood_high` by the daemon — read-only consumer.
- `DynamicPlaylist` parser extensions (numeric operators) — unrelated.

## 7. Conventions & deploy

Branch `feat/mood-range-filter` off `develop`. black + isort at **line length 80**
(pyproject). Tests: MariaDB container (`db_container.sh` flow) +
`~/.virtualenvs/wickedjukebox/bin/pytest` from repo root; suite is 90 passed pre-feature.
Deploy: `pip install .` + restart the channel daemon; config unchanged.
