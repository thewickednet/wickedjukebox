# Candidate-pool optimization for `smart_prefetch` (toggleable) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cut the smart picker's mood-off pick from an O(N) full-table filesort (~0.5s on prod/73k) to O(K) by scoring only a random id-pool, behind a per-channel `candidate_pool_size` config toggle that defaults to today's behavior.

**Architecture:** In `find_song`, when no mood window bounds the scan and pooling is enabled, filter the existing scoring query to a random `id IN (pool)` and take the pick; fall through to the unchanged full-table path if the pool matches nothing (never silent). The pool size comes from a new optional config key read via the config abstraction (approach b — not in `CONFIG_KEYS`, so no config migration).

**Tech Stack:** Python 3.10, SQLAlchemy < 2.0, MariaDB, pytest.

## Global Constraints

- **SQLAlchemy pinned `< 2.0`** — 1.4-style query API.
- **Toggle defaults to current behavior:** `candidate_pool_size` absent or `0` → `find_song` behaves exactly as today. `find_song` reads it via `scoring_config.get(ScoringConfig.CANDIDATE_POOL_SIZE, 0)` so existing callers/tests (which omit it) are unaffected.
- **Approach (b) config read:** add `ConfigKeys.CANDIDATE_POOL_SIZE` and read it with `Config.get(..., fallback=0, converter=int)`. Do **NOT** add `candidate_pool_size` to `SmartPrefetch.CONFIG_KEYS` (`Config.dictify` requires every `CONFIG_KEYS` entry to be present; keeping it out avoids forcing a config line into existing deployments).
- **Pool only when mood is off:** apply the pool only when `mood_range is None` for that pick. A mood window already bounds the scan via `song_mood_score_idx`; leave that path untouched (confirmed with the user).
- **Never silent / never worse than today:** a pooled pick that matches nothing falls through to the current full-table behavior (which keeps its own mood→unfiltered fallback).
- **Scope:** `find_song` + config wiring only. Do NOT touch `Song.random` (quick startup path), the `DynamicPlaylist` bug, or scoring weights.
- **Formatting:** black + isort, **line-length 80**, pinned **black 23.3.0 / isort 5.12.0**.
- **Spec:** `docs/superpowers/specs/2026-07-12-candidate-pool-smart-random-design.md`.

## Environment (already provisioned — verify, don't rebuild unless broken)

- **Venv:** `~/.virtualenvs/wickedjukebox/bin/{python,pytest}` (`fab` not installed).
- **DB:** the daemon test suite runs against the DSN in `.wicked/wickedjukebox/config.ini` `[core] dsn` (currently the MariaDB container `jukeboxdb_idx` on host port 33066, database `jukebox`, holding the reconciled alembic baseline). `conftest.py` runs `alembic upgrade head` at session start and rolls back each test in a transaction (fixtures `dbsession`, `default_data`). Docker via `DOCKER_HOST=unix:///var/run/docker.sock` if you need to check the container.
- **Pinned formatters:** `/tmp/wjfmt/bin/{black,isort}` (recreate if missing: `python -m venv /tmp/wjfmt && /tmp/wjfmt/bin/pip -q install black==23.3.0 isort==5.12.0`).
- **Run tests:** full suite `~/.virtualenvs/wickedjukebox/bin/pytest -q`; single file `… pytest test/test_prefetcher.py -v`.

**Baseline:** run `~/.virtualenvs/wickedjukebox/bin/pytest -q 2>&1 | tail -1` first and note the count (should be 120 passing). The only delta at the end is the new tests.

---

## File Structure

- `wickedjukebox/core/smartfind.py` — `ScoringConfig.CANDIDATE_POOL_SIZE`, `_random_id_pool()`, `_finalize()`, the pooled fast-path in `find_song` (Task 1).
- `wickedjukebox/config.py` — `ConfigKeys.CANDIDATE_POOL_SIZE` (Task 2).
- `wickedjukebox/component/random.py` — `SmartPrefetch.configure()` reads the key into `scoring_config`; docstring (Task 2).
- `config.ini.dist` — document the key (Task 2).
- `test/test_prefetcher.py` — new tests (both tasks).

---

## Task 1: Pooled fast-path in `find_song`

**Files:**
- Modify: `wickedjukebox/core/smartfind.py`
- Test: `test/test_prefetcher.py`

**Interfaces:**
- Produces: `ScoringConfig.CANDIDATE_POOL_SIZE` (enum member, value `"candidate_pool_size"`); module functions `smartfind._random_id_pool(session, size) -> List[int]` and `smartfind._finalize(session, candidate) -> Optional[Song]`. `find_song` now honors `scoring_config.get(ScoringConfig.CANDIDATE_POOL_SIZE, 0)`.
- Consumes: nothing new.

- [ ] **Step 1: Write the failing tests**

Append to `test/test_prefetcher.py` (it already imports `find_song`, `ScoringConfig`, `Song`, `Channel`, `User`, and defines `SCORING_CONFIG`). Add this import near the top with the other imports:

```python
from wickedjukebox.core import smartfind
```

Then append these tests:

```python
def _pool_cfg(size):
    return {**SCORING_CONFIG, ScoringConfig.CANDIDATE_POOL_SIZE: size}


def test_find_song_pool_returns_song(
    dbsession: Session, default_data: Dict[str, Any]
):
    """With pooling on and no mood window, a pick is still returned."""
    song = find_song(dbsession, _pool_cfg(500), True)
    assert song is not None
    assert song.id == default_data["default_song"].id


def test_find_song_pool_disabled_is_unchanged(
    dbsession: Session, default_data: Dict[str, Any]
):
    """pool size 0 -> original behavior (returns the eligible song)."""
    song = find_song(dbsession, _pool_cfg(0), True)
    assert song is not None
    assert song.id == default_data["default_song"].id


def test_find_song_pool_never_silent_on_pool_miss(
    dbsession: Session, default_data: Dict[str, Any], monkeypatch
):
    """If the random pool matches nothing, fall through to the full pick."""
    monkeypatch.setattr(smartfind, "_random_id_pool", lambda *a, **k: [10**9])
    song = find_song(dbsession, _pool_cfg(500), True)
    assert song is not None
    assert song.id == default_data["default_song"].id


def test_pool_used_when_mood_off(
    dbsession: Session, default_data: Dict[str, Any], monkeypatch
):
    """No mood window -> the pool path runs."""
    calls = []
    real = smartfind._random_id_pool
    monkeypatch.setattr(
        smartfind,
        "_random_id_pool",
        lambda s, n: calls.append(n) or real(s, n),
    )
    find_song(dbsession, _pool_cfg(500), True)  # no channel_name -> mood off
    assert calls, "pool should be drawn when no mood window is active"


def test_pool_skipped_when_mood_active(
    dbsession: Session, default_data: Dict[str, Any], monkeypatch
):
    """An active mood window bounds the scan already -> pool path is skipped."""
    default_data["default_channel"].mood_low = 10
    default_data["default_channel"].mood_high = 90
    dbsession.flush()
    calls = []
    monkeypatch.setattr(
        smartfind, "_random_id_pool", lambda *a, **k: calls.append(1) or []
    )
    song = find_song(
        dbsession, _pool_cfg(500), True, channel_name="test-channel"
    )
    assert song is not None
    assert calls == [], "pool must not be drawn when a mood window is active"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `~/.virtualenvs/wickedjukebox/bin/pytest test/test_prefetcher.py -k pool -v`
Expected: errors/failures — `ScoringConfig` has no `CANDIDATE_POOL_SIZE` and `smartfind._random_id_pool` does not exist yet.

- [ ] **Step 3: Add the enum member and `import random`**

In `wickedjukebox/core/smartfind.py`, add `import random` under `import logging` (line ~6). Then add the enum member to `ScoringConfig`:

```python
    MAX_DURATION = "max_duration"
    PROOF_OF_LIFE_TIMEOUT = "proof_of_life"
```
becomes:
```python
    MAX_DURATION = "max_duration"
    PROOF_OF_LIFE_TIMEOUT = "proof_of_life"
    #: 0 (or absent) = disabled (score the whole table). >0 = score only a
    #: random pool of this many candidate ids (fast, flat with library size).
    CANDIDATE_POOL_SIZE = "candidate_pool_size"
```

Also add `List` to the typing import:
```python
from typing import TYPE_CHECKING, Any, Mapping, Optional
```
becomes:
```python
from typing import TYPE_CHECKING, Any, List, Mapping, Optional
```

- [ ] **Step 4: Add the `_random_id_pool` and `_finalize` helpers**

In `wickedjukebox/core/smartfind.py`, immediately **before** `def find_song(` (line ~194), insert:

```python
def _random_id_pool(session: orm.Session, size: int) -> List[int]:
    """
    Return up to *size* distinct random song ids drawn uniformly from the
    ``[MIN(id), MAX(id)]`` range (two indexed lookups; effectively free). The
    caller scores only these ids instead of the whole table. Id gaps and later
    filters trim the set slightly, which is fine.
    """
    min_id, max_id = session.query(
        func.min(Song.id), func.max(Song.id)
    ).one()
    if min_id is None or max_id is None:
        return []
    if min_id >= max_id:
        return [int(min_id)]
    return list({random.randint(min_id, max_id) for _ in range(size)})


def _finalize(session: orm.Session, candidate: Any) -> Optional[Song]:
    """
    Turn a scored candidate row into a Song (closing the session), mirroring the
    original find_song tail. Returns None when there is no usable candidate.
    """
    if candidate is None:
        return None
    try:
        if not candidate.score:
            # no users are online!
            session.close()
            return None
        out = (candidate.id, candidate.localpath, float(candidate.score))
        LOG.info("Selected song (%d, %s) via smartget. Score was %4.3f", *out)
        selected_song = session.query(Song).filter(Song.id == out[0]).first()
        session.close()
        return selected_song
    except IndexError:
        LOG.warning(
            "No song returned from query. Is the database empty?", exc_info=True
        )
        session.close()
        return None
```

- [ ] **Step 5: Rewrite the tail of `find_song` to add the pooled fast-path**

In `wickedjukebox/core/smartfind.py`, replace this block (currently lines ~255-300, from the `broken` filter through the end of the function):

```python
    query = query.filter(not_(Song.broken))  # type: ignore
    query = query.filter(not_(Song.exclude_from_random))  # type: ignore
    query = DynamicPlaylist.apply_to(query)  # type: ignore
    unfiltered_query = query
    mood_range = (
        Channel.mood_range(session, channel_name) if channel_name else None
    )
    if mood_range is not None:
        low, high = mood_range
        query = query.filter(
            or_(
                Song.mood_score.is_(None),
                Song.mood_score.between(low, high),
            )
        )
    query = query.limit(10)  # type: ignore
    query = query.offset(0)  # type: ignore
    candidate = query.first()

    if candidate is None and mood_range is not None:
        LOG.info(
            "No candidates inside mood range %r; falling back to an "
            "unfiltered pick",
            mood_range,
        )
        candidate = unfiltered_query.limit(10).offset(0).first()

    if candidate is None:
        return None

    try:
        if not candidate.score:
            # no users are online!
            session.close()
            return None
        out = (candidate.id, candidate.localpath, float(candidate.score))
        LOG.info("Selected song (%d, %s) via smartget. Score was %4.3f", *out)
        selected_song = session.query(Song).filter(Song.id == out[0]).first()
        session.close()
        return selected_song
    except IndexError:
        LOG.warning(
            "No song returned from query. Is the database empty?", exc_info=True
        )
        session.close()
        return None
```

with:

```python
    query = query.filter(not_(Song.broken))  # type: ignore
    query = query.filter(not_(Song.exclude_from_random))  # type: ignore
    query = DynamicPlaylist.apply_to(query)  # type: ignore
    unfiltered_query = query
    mood_range = (
        Channel.mood_range(session, channel_name) if channel_name else None
    )

    # Candidate-pool fast-path: when no mood window bounds the scan and pooling
    # is enabled, score only a bounded random id-pool instead of the whole
    # table (O(pool) instead of O(N)). If the pool yields a song, use it;
    # otherwise fall through to the unchanged full-table behaviour so a pick is
    # never silent. When a mood window IS active it already bounds the scan via
    # the mood index, so that path is left untouched.
    pool_size = scoring_config.get(ScoringConfig.CANDIDATE_POOL_SIZE, 0)
    if pool_size and mood_range is None:
        pool = _random_id_pool(session, pool_size)
        if pool:
            pooled_candidate = (
                unfiltered_query.filter(Song.id.in_(pool))  # type: ignore
                .limit(10)
                .offset(0)
                .first()
            )
            if pooled_candidate is not None:
                return _finalize(session, pooled_candidate)

    if mood_range is not None:
        low, high = mood_range
        query = query.filter(
            or_(
                Song.mood_score.is_(None),
                Song.mood_score.between(low, high),
            )
        )
    query = query.limit(10)  # type: ignore
    query = query.offset(0)  # type: ignore
    candidate = query.first()

    if candidate is None and mood_range is not None:
        LOG.info(
            "No candidates inside mood range %r; falling back to an "
            "unfiltered pick",
            mood_range,
        )
        candidate = unfiltered_query.limit(10).offset(0).first()

    return _finalize(session, candidate)
```

Note: `scoring_config` is a `Mapping`, so `.get(..., 0)` is valid and returns 0 when the key is absent (existing callers unaffected).

- [ ] **Step 6: Run the pool tests, then the full suite**

```bash
~/.virtualenvs/wickedjukebox/bin/pytest test/test_prefetcher.py -k pool -v
~/.virtualenvs/wickedjukebox/bin/pytest -q 2>&1 | tail -3
```
Expected: the 5 pool tests pass; full suite = baseline (120) + 5 = **125 passing, 0 failures**.

- [ ] **Step 7: Format and commit**

```bash
/tmp/wjfmt/bin/isort --profile black --line-length 80 wickedjukebox/core/smartfind.py test/test_prefetcher.py
/tmp/wjfmt/bin/black --line-length 80 wickedjukebox/core/smartfind.py test/test_prefetcher.py
git add wickedjukebox/core/smartfind.py test/test_prefetcher.py
git -c commit.gpgsign=false commit -m "feat(smartfind): candidate-pool fast-path in find_song (mood-off, toggleable)

Score only a random id-pool when no mood window bounds the scan and
CANDIDATE_POOL_SIZE>0; fall through to the full-table pick if the pool matches
nothing (never silent). Pool skipped when a mood window is active. Disabled by
default (scoring_config.get(..., 0)).

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: Config wiring for `candidate_pool_size` (approach b)

**Files:**
- Modify: `wickedjukebox/config.py`, `wickedjukebox/component/random.py`, `config.ini.dist`
- Test: `test/test_prefetcher.py`

**Interfaces:**
- Consumes: `ScoringConfig.CANDIDATE_POOL_SIZE` (Task 1).
- Produces: `ConfigKeys.CANDIDATE_POOL_SIZE`; `SmartPrefetch.configure()` now populates `scoring_config[ScoringConfig.CANDIDATE_POOL_SIZE]` from config (0 if absent).

- [ ] **Step 1: Write the failing config test**

Append to `test/test_prefetcher.py` (add `from configparser import ConfigParser` and `from wickedjukebox.config import Config, ConfigKeys` to the imports):

```python
def test_candidate_pool_size_optional_read():
    """Approach (b): the key is read with a fallback, so a section without it
    still yields 0 (no ConfigError), and a set value parses as int."""
    cp = ConfigParser()
    cp.add_section("channel:test:autoplay")
    cp.set("channel:test:autoplay", "type", "smart_prefetch")
    cfg = Config(cp)
    assert (
        cfg.get(
            ConfigKeys.CANDIDATE_POOL_SIZE,
            fallback=0,
            channel="test",
            converter=int,
        )
        == 0
    )
    cp.set("channel:test:autoplay", "candidate_pool_size", "500")
    assert (
        cfg.get(
            ConfigKeys.CANDIDATE_POOL_SIZE,
            fallback=0,
            channel="test",
            converter=int,
        )
        == 500
    )
```

- [ ] **Step 2: Run it to verify it fails**

Run: `~/.virtualenvs/wickedjukebox/bin/pytest test/test_prefetcher.py::test_candidate_pool_size_optional_read -v`
Expected: `AttributeError: CANDIDATE_POOL_SIZE` — the `ConfigKeys` member does not exist yet.

- [ ] **Step 3: Add the `ConfigKeys` member**

In `wickedjukebox/config.py`, in the `ConfigKeys` enum (after `JINGLE`, line ~91):

```python
    JINGLE = ConfigOption(ConfigScope.CHANNEL, "jingle", "type")
```
becomes:
```python
    JINGLE = ConfigOption(ConfigScope.CHANNEL, "jingle", "type")
    CANDIDATE_POOL_SIZE = ConfigOption(
        ConfigScope.CHANNEL, "autoplay", "candidate_pool_size"
    )
```

- [ ] **Step 4: Read it in `SmartPrefetch.configure` (do NOT add to `CONFIG_KEYS`)**

In `wickedjukebox/component/random.py`, in `SmartPrefetch.configure`, add the pool size to the `scoring_config` dict (leave `CONFIG_KEYS` unchanged). Change:

```python
            ScoringConfig.SONG_AGE: int(cfg["weight_song_age"]),
            ScoringConfig.USER_RATING: int(cfg["weight_user_rating"]),
        }
```
to:
```python
            ScoringConfig.SONG_AGE: int(cfg["weight_song_age"]),
            ScoringConfig.USER_RATING: int(cfg["weight_user_rating"]),
            ScoringConfig.CANDIDATE_POOL_SIZE: self._config.get(
                ConfigKeys.CANDIDATE_POOL_SIZE,
                fallback=0,
                channel=self.channel_name,
                converter=int,
            ),
        }
```
(`ConfigKeys` and `ScoringConfig` are already imported in this module; `self._config` is always a `Config`.)

- [ ] **Step 5: Document the key (docstring + config.ini.dist)**

In `wickedjukebox/component/random.py`, in the `SmartPrefetch` class docstring's ini example, add after the `max_duration` line:

```
        ; No songs longer than this amount of seconds is returned
        max_duration = 600
```
becomes:
```
        ; No songs longer than this amount of seconds is returned
        max_duration = 600

        ; Bound the "smart random" scan to a random pool of this many candidate
        ; songs (fast + flat as the library grows). 0 or omitted = disabled
        ; (score the whole table). Only applies when no mood window is active.
        candidate_pool_size = 500
```

In `config.ini.dist`, in `[channel:wicked:autoplay]`, after `weight_user_rating = 4` add:

```ini
; Bound the smart-random scan to a random pool of this many candidate songs
; (fast, flat with library size). 0 or omitted = disabled (whole-table scan).
; Only applies when the channel has no active mood window.
candidate_pool_size = 0
```

- [ ] **Step 6: Run the config test, then the full suite**

```bash
~/.virtualenvs/wickedjukebox/bin/pytest test/test_prefetcher.py::test_candidate_pool_size_optional_read -v
~/.virtualenvs/wickedjukebox/bin/pytest -q 2>&1 | tail -3
```
Expected: config test passes; full suite = **126 passing, 0 failures** (125 + 1).

- [ ] **Step 7: Format and commit**

```bash
/tmp/wjfmt/bin/isort --profile black --line-length 80 wickedjukebox/config.py wickedjukebox/component/random.py test/test_prefetcher.py
/tmp/wjfmt/bin/black --line-length 80 wickedjukebox/config.py wickedjukebox/component/random.py test/test_prefetcher.py
git add wickedjukebox/config.py wickedjukebox/component/random.py config.ini.dist test/test_prefetcher.py
git -c commit.gpgsign=false commit -m "feat(config): wire candidate_pool_size into smart_prefetch (approach b)

Add ConfigKeys.CANDIDATE_POOL_SIZE; SmartPrefetch.configure reads it optionally
(fallback 0, not in CONFIG_KEYS -> no config migration) into scoring_config.
Document the key in the SmartPrefetch docstring and config.ini.dist.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review (completed by plan author)

**1. Spec coverage:**
- Toggle `candidate_pool_size`, approach (b), not in CONFIG_KEYS → Task 2 Steps 3-4. ✔
- Pooled fast-path, pool-only-when-mood-off, never-silent fall-through → Task 1 Step 5. ✔
- `draw_pool` off MIN/MAX(id) → Task 1 Step 4 (`_random_id_pool`). ✔
- Default-behavior-when-disabled via `.get(..., 0)` → Task 1 Step 5 + `test_find_song_pool_disabled_is_unchanged`. ✔
- Docs (docstring + config.ini.dist) → Task 2 Step 5. ✔
- Tests: pooled pick, disabled=current, never-silent, mood-off-uses / mood-on-skips, config read → Tasks 1 & 2. ✔
- Non-goals (Song.random, DynamicPlaylist, weights) → Global Constraints (do-not-touch). ✔

**2. Placeholder scan:** none — every step has exact before/after code and exact commands.

**3. Type/name consistency:** `ScoringConfig.CANDIDATE_POOL_SIZE` (value `"candidate_pool_size"`), `ConfigKeys.CANDIDATE_POOL_SIZE`, `_random_id_pool`, `_finalize` are used identically across `find_song`, the tests (monkeypatch targets), and Task 2's wiring.

## Notes / risks

- `_random_id_pool` with a single-row test DB returns `[that id]` (min == max), so `test_find_song_pool_returns_song` is deterministic. Multi-row pool randomness is only exercised via the monkeypatched tests, keeping the suite deterministic.
- The pooled path reuses `unfiltered_query` (broken/exclude/dynamicPlaylist filters, no mood) — correct, because the pool only runs when `mood_range is None`.
- `_finalize` closes the session (as the original tail did); the pooled path only calls it when it has a candidate, so the fall-through path still has an open session.
