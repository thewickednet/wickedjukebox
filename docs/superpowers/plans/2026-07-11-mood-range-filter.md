# Mood Range Filter Implementation Plan (wickedjukebox)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Honor the per-channel mood window (`channel.mood_low`/`mood_high`) in both random
pickers, per the contract in djukebox's `docs/integration-contract.md` §13.

**Architecture:** Map the Django-created columns into the SQLAlchemy models (+ one alembic
parity migration for dev/test DBs), add a `Channel.mood_range` per-pick reader, thread the
channel into `find_song`/`Song.random` with a NULL-passes filter and unfiltered fallback,
and give `AllFilesRandom` a best-effort rejection-sampling DB check.

**Tech Stack:** Python 3.10+ (venv is 3.13), SQLAlchemy 1.4 (pinned < 2.0), alembic,
pytest against a live MariaDB container.

**Spec:** `docs/superpowers/specs/2026-07-11-mood-range-filter-design.md`

## Global Constraints

- Repo: `/home/wickeddoc/workspace/private/wickedjukebox`, branch `feat/mood-range-filter`
  off `develop`. This is NOT the djukebox repo — different conventions apply.
- Python/tools: `~/.virtualenvs/wickedjukebox/bin/{python,pytest,black,isort}`.
- **Tests need the live MariaDB container.** It is already running (`docker ps` shows
  `jukeboxdb`; `.wicked/wickedjukebox/config.ini` has the correct DSN). Run tests from the
  repo root: `~/.virtualenvs/wickedjukebox/bin/pytest <path>` (conftest reads the DSN from
  the config and runs `alembic upgrade head` itself). Baseline: 90 passed. If the DB is
  down, report BLOCKED — do not try to re-create it.
- **Line length 80** (pyproject black + isort, black profile). Run `black` and `isort` on
  every touched file INCLUDING tests (this repo formats tests too; only `demon*` legacy
  files are excluded).
- Contract semantics, verbatim: thresholds read fresh per pick; filter
  `mood_score IS NULL OR mood_score BETWEEN low AND high` (NULL always passes); empty
  filtered pool → unfiltered fallback, never silence; the daemon never writes these
  columns.
- Names verbatim: `Song.mood_score`, `Channel.mood_low`, `Channel.mood_high`,
  `Channel.mood_range(session, name)`, `find_song(..., channel_name=None)`,
  `Song.random(..., mood_range=None)`, module constant `MOOD_SAMPLE_SIZE = 50`, alembic
  revision `e8f2a4c6d0b1` (down_revision `c7a1e9b4f2d3`).
- Commits: `git commit --no-gpg-sign`, conventional prefix (`feat:`/`test:`), message ends
  with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`. Never push.

**Setup (before Task 1):** in the wickedjukebox repo, from `develop`:
`git checkout -b feat/mood-range-filter`.

---

### Task 1: ORM columns, alembic parity migration, `Channel.mood_range`

**Files:**
- Modify: `wickedjukebox/model/db/library.py` (~line 241, after `replaygain_written`)
- Modify: `wickedjukebox/model/db/playback.py` (imports ~line 23-37; Channel class
  ~line 51-74)
- Create: `alembic/versions/e8f2a4c6d0b1_mood_range_parity.py`
- Test: append to `test/test_prefetcher.py`

**Interfaces:**
- Produces: `Channel.mood_range(session, name) -> Optional[Tuple[int, int]]`;
  `Song.mood_score` / `Channel.mood_low` / `Channel.mood_high` mapped columns. Tasks 2-3
  consume all of these.

- [ ] **Step 1: Write the failing tests**

Append to `test/test_prefetcher.py`:

```python
def test_channel_mood_range_unknown_channel(
    dbsession: Session, default_data: Dict[str, Any]
):
    """An unknown channel name means no filtering."""
    assert Channel.mood_range(dbsession, "no-such-channel") is None


def test_channel_mood_range_off(
    dbsession: Session, default_data: Dict[str, Any]
):
    """Both thresholds NULL (the default) means filtering is off."""
    assert Channel.mood_range(dbsession, "test-channel") is None


def test_channel_mood_range_half_set(
    dbsession: Session, default_data: Dict[str, Any]
):
    """A half-set window (only one threshold) is treated as off."""
    default_data["default_channel"].mood_low = 10
    dbsession.flush()
    assert Channel.mood_range(dbsession, "test-channel") is None


def test_channel_mood_range_active(
    dbsession: Session, default_data: Dict[str, Any]
):
    """Both thresholds set: the window is returned as a tuple."""
    default_data["default_channel"].mood_low = 10
    default_data["default_channel"].mood_high = 90
    dbsession.flush()
    assert Channel.mood_range(dbsession, "test-channel") == (10, 90)
```

Add the import at the top of the file, after the existing
`from wickedjukebox.model.db.library import Song` line:

```python
from wickedjukebox.model.db.playback import Channel
```

- [ ] **Step 2: Run to verify failure**

Run: `~/.virtualenvs/wickedjukebox/bin/pytest test/test_prefetcher.py -q` (repo root)
Expected: the 4 new tests ERROR/FAIL — `Channel` has no attribute `mood_range` (and the
columns don't exist yet); the 12 pre-existing tests still pass.

- [ ] **Step 3: Add the mapped columns**

`wickedjukebox/model/db/library.py` — directly after the `replaygain_written` line
(~line 241), add:

```python
    # Composite energy score 0-100 (chill -> intense) computed by djukebox
    # from bpm/loudness/crest_factor; NULL = not yet analyzed. Read-only for
    # the daemon (see docs/superpowers/specs/2026-07-11-mood-range-filter-…).
    mood_score = Column(SmallInteger)
```

`wickedjukebox/model/db/playback.py` — two edits:

1. Extend the `from sqlalchemy import (...)` block with `SmallInteger` (alphabetical,
   between `Integer` and `String`), and the `from typing import Optional` line becomes:

```python
from typing import Optional, Tuple
```

2. In `class Channel`, after the `owner_id` line (~line 61), add:

```python
    # Randomizer mood window (0-100), written by the djukebox web UI. Both
    # NULL = mood filtering off. Read fresh per pick via Channel.mood_range.
    mood_low = Column(SmallInteger)
    mood_high = Column(SmallInteger)
```

and after the `by_name` staticmethod (~line 74), add:

```python
    @staticmethod
    def mood_range(
        session: TSession, name: str
    ) -> Optional[Tuple[int, int]]:
        """
        The live randomizer mood window for the named channel.

        Returns ``(low, high)`` when both thresholds are set (apply as
        ``mood_score IS NULL OR mood_score BETWEEN low AND high`` — see the
        djukebox integration contract), or ``None`` when filtering is off or
        the channel is unknown. Read this fresh on every pick so threshold
        changes from the web UI apply immediately.
        """
        channel = Channel.by_name(session, name)
        if (
            channel is None
            or channel.mood_low is None
            or channel.mood_high is None
        ):
            return None
        return (channel.mood_low, channel.mood_high)
```

- [ ] **Step 4: Create the alembic parity migration**

Create `alembic/versions/e8f2a4c6d0b1_mood_range_parity.py`:

```python
# type: ignore
# pylint: skip-file
"""mood range parity

Map the mood columns created by djukebox (Django migrations 0042/0043) into
the alembic-managed schema: song.mood_score (composite energy score 0-100,
computed by djukebox) and channel.mood_low/mood_high (the randomizer mood
window). Production already has these columns (its schema is Django-managed)
— this migration only serves alembic-built dev/test databases, exactly like
the djukebox_field_parity precedent (b3d9f1a2c4e6).

Revision ID: e8f2a4c6d0b1
Revises: c7a1e9b4f2d3
Create Date: 2026-07-11
"""

import sqlalchemy as sa

from alembic import op

revision = "e8f2a4c6d0b1"
down_revision = "c7a1e9b4f2d3"


def upgrade():
    op.add_column(
        "song", sa.Column("mood_score", sa.SmallInteger(), nullable=True)
    )
    op.create_index(
        "song_mood_score_idx", "song", ["mood_score"], unique=False
    )
    op.add_column(
        "channel", sa.Column("mood_low", sa.SmallInteger(), nullable=True)
    )
    op.add_column(
        "channel", sa.Column("mood_high", sa.SmallInteger(), nullable=True)
    )


def downgrade():
    op.drop_column("channel", "mood_high")
    op.drop_column("channel", "mood_low")
    op.drop_index("song_mood_score_idx", table_name="song")
    op.drop_column("song", "mood_score")
```

- [ ] **Step 5: Run the tests**

Run: `~/.virtualenvs/wickedjukebox/bin/pytest test/test_prefetcher.py -q`
Expected: **16 passed** (12 old + 4 new). Note: conftest applies `alembic upgrade head`
per session — the new migration runs automatically. If it errors with "Duplicate column",
the container DB already got the columns from a previous partial run; that is fine only if
tests then pass; otherwise report the error verbatim.

- [ ] **Step 6: Format + commit**

Run: `~/.virtualenvs/wickedjukebox/bin/black wickedjukebox/model/db/library.py wickedjukebox/model/db/playback.py alembic/versions/e8f2a4c6d0b1_mood_range_parity.py test/test_prefetcher.py && ~/.virtualenvs/wickedjukebox/bin/isort wickedjukebox/model/db/library.py wickedjukebox/model/db/playback.py alembic/versions/e8f2a4c6d0b1_mood_range_parity.py test/test_prefetcher.py`
Expected: no changes (code above is pre-formatted for 80 cols); if reformatted, re-run the
tests.

```bash
git add wickedjukebox/model/db/library.py wickedjukebox/model/db/playback.py \
  alembic/versions/e8f2a4c6d0b1_mood_range_parity.py test/test_prefetcher.py
git commit --no-gpg-sign -m "feat: map mood columns + Channel.mood_range per-pick reader

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Mood filter in `find_song` and `Song.random`, threaded from the prefetcher

**Files:**
- Modify: `wickedjukebox/core/smartfind.py` (imports ~lines 14-18; `find_song`
  ~lines 194-259)
- Modify: `wickedjukebox/model/db/library.py` (imports ~lines 26-45; `Song.random`
  ~lines 285-302)
- Modify: `wickedjukebox/component/random.py` (`SmartPrefetchThread.run` ~lines 156-190;
  `SmartPrefetch` class docstring ~line 209-211)
- Test: append to `test/test_prefetcher.py`

**Interfaces:**
- Consumes: `Channel.mood_range(session, name)` (Task 1).
- Produces: `find_song(session, scoring_config, is_mysql, channel_name=None)`;
  `Song.random(session, max_duration=None, mood_range=None)`. Task 3 reuses the same
  contract semantics but not these functions.

- [ ] **Step 1: Write the failing tests**

Append to `test/test_prefetcher.py` (uses the `Channel` import and helpers from Task 1):

```python
def _add_song(
    dbsession: Session,
    default_data: Dict[str, Any],
    localpath: str,
    mood_score,
):
    """Insert a second eligible song with the given mood score."""
    song = Song(localpath=localpath)
    song.artist = default_data["default_artist"]
    song.album = default_data["default_album"]
    song.title = localpath
    song.duration = 300
    song.mood_score = mood_score
    dbsession.add(song)
    dbsession.flush()
    return song


def _window(dbsession: Session, default_data: Dict[str, Any], low, high):
    default_data["default_channel"].mood_low = low
    default_data["default_channel"].mood_high = high
    dbsession.flush()


def test_find_song_mood_filters_out_of_range(
    dbsession: Session, default_data: Dict[str, Any]
):
    """With an active window, only in-range songs are candidates."""
    default_data["default_song"].mood_score = 95
    in_range = _add_song(dbsession, default_data, "in-range.mp3", 50)
    _window(dbsession, default_data, 20, 80)
    song = find_song(
        dbsession, SCORING_CONFIG, True, channel_name="test-channel"
    )
    assert song is not None
    assert song.id == in_range.id


def test_find_song_mood_null_passes(
    dbsession: Session, default_data: Dict[str, Any]
):
    """A song without a mood score always passes an active window."""
    _window(dbsession, default_data, 20, 80)
    song = find_song(
        dbsession, SCORING_CONFIG, True, channel_name="test-channel"
    )
    assert song is not None


def test_find_song_mood_fallback_never_silent(
    dbsession: Session, default_data: Dict[str, Any]
):
    """All songs outside the window: fall back to an unfiltered pick."""
    default_data["default_song"].mood_score = 95
    _window(dbsession, default_data, 20, 80)
    song = find_song(
        dbsession, SCORING_CONFIG, True, channel_name="test-channel"
    )
    assert song is not None
    assert song.id == default_data["default_song"].id


def test_find_song_without_channel_does_not_filter(
    dbsession: Session, default_data: Dict[str, Any]
):
    """No channel_name (legacy callers): mood filtering is off."""
    default_data["default_song"].mood_score = 95
    _window(dbsession, default_data, 20, 80)
    song = find_song(dbsession, SCORING_CONFIG, True)
    assert song is not None


def test_random_mood_filters_out_of_range(
    dbsession: Session, default_data: Dict[str, Any]
):
    default_data["default_song"].mood_score = 95
    in_range = _add_song(dbsession, default_data, "in-range2.mp3", 50)
    dbsession.flush()
    song = Song.random(dbsession, mood_range=(20, 80))
    assert song is not None
    assert song.id == in_range.id


def test_random_mood_null_passes(
    dbsession: Session, default_data: Dict[str, Any]
):
    song = Song.random(dbsession, mood_range=(20, 80))
    assert song is not None
    assert song.id == default_data["default_song"].id


def test_random_mood_fallback_never_silent(
    dbsession: Session, default_data: Dict[str, Any]
):
    default_data["default_song"].mood_score = 95
    dbsession.flush()
    song = Song.random(dbsession, mood_range=(20, 80))
    assert song is not None
    assert song.id == default_data["default_song"].id


def test_random_no_mood_range_unfiltered(
    dbsession: Session, default_data: Dict[str, Any]
):
    default_data["default_song"].mood_score = 95
    dbsession.flush()
    song = Song.random(dbsession)
    assert song is not None
```

- [ ] **Step 2: Run to verify failure**

Run: `~/.virtualenvs/wickedjukebox/bin/pytest test/test_prefetcher.py -q`
Expected: the new tests fail — `find_song() got an unexpected keyword argument
'channel_name'` / `Song.random() got an unexpected keyword argument 'mood_range'`.

- [ ] **Step 3: Implement `find_song`**

`wickedjukebox/core/smartfind.py`:

1. Change the expression import (~line 14) to:

```python
from sqlalchemy.sql.expression import and_, or_, text
```

2. Change the playback import (~line 18) to:

```python
from wickedjukebox.model.db.playback import Channel, DynamicPlaylist
```

3. Change the `find_song` signature (~lines 194-198) to:

```python
def find_song(
    session: orm.Session,
    scoring_config: Mapping[ScoringConfig, int],
    is_mysql: bool,
    channel_name: Optional[str] = None,
) -> Optional[Song]:
```

4. Replace the filter/limit block (~lines 254-262, from `query = query.filter(not_(Song.broken))`
   through `if candidate is None: return None`) with:

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
```

- [ ] **Step 4: Implement `Song.random`**

`wickedjukebox/model/db/library.py`:

1. Extend the sqlalchemy import block (~lines 26-45) with `or_` (alphabetical, after
   `not_`), and the typing import (~line 24) becomes:

```python
from typing import Optional, Tuple
```

2. Replace the whole `random` staticmethod (~lines 285-302) with:

```python
    @staticmethod
    def random(
        session: TSession,
        max_duration: Optional[int] = None,
        mood_range: Optional[Tuple[int, int]] = None,
    ) -> Optional["Song"]:
        """
        Retrieve a random song eligible for autoplay.

        Songs flagged ``broken`` or ``exclude_from_random`` are never
        returned. When *max_duration* is given, songs longer than that many
        seconds are also excluded. When *mood_range* is given, only songs
        whose ``mood_score`` is NULL (not yet analyzed) or inside the window
        qualify — unless nothing does, in which case the window is dropped
        so a pick never comes up empty. Returns ``None`` if nothing
        qualifies at all.
        """
        query = session.query(Song)
        query = query.filter(not_(Song.broken))
        query = query.filter(not_(Song.exclude_from_random))
        if max_duration is not None:
            query = query.filter(Song.duration < max_duration)
        unfiltered_query = query
        if mood_range is not None:
            low, high = mood_range
            query = query.filter(
                or_(
                    Song.mood_score.is_(None),
                    Song.mood_score.between(low, high),
                )
            )
        song = query.order_by(func.rand()).first()
        if song is None and mood_range is not None:
            song = unfiltered_query.order_by(func.rand()).first()
        return song
```

- [ ] **Step 5: Thread the channel through the prefetcher**

`wickedjukebox/component/random.py`:

1. Add the playback import after the existing library import (~line 18):

```python
from wickedjukebox.model.db.playback import Channel
```

2. In `SmartPrefetchThread.run`, replace the quick-prefetch block (~lines 158-172) with:

```python
        with Session() as session:  # type: ignore
            # We use a "naive" random first so we have something quickly. The
            # "smart" query is much slower.
            mood_range = Channel.mood_range(session, self.channel_name)
            song = Song.random(  # type: ignore
                session,
                self.scoring_config[ScoringConfig.MAX_DURATION],
                mood_range=mood_range,
            )
            if song is None:
                self._log.error(
                    "Unable to prefetch a song using pure random. Is the DB "
                    "empty?"
                )
                return
            self._log.debug("Quick prefetch found song %r", song)
            self.queue.put(abspath(song.localpath), block=True, timeout=None)
```

3. In the smart loop (~lines 185-190), replace the `find_song(...)` call with:

```python
            with Session() as session:  # type: ignore
                song = find_song(
                    session,  # type: ignore
                    self.scoring_config,
                    is_mysql,
                    channel_name=self.channel_name,
                )
```

4. In the `SmartPrefetch` class docstring, after the sentence "So the *exact* calculation
   is always off by one \"play\"." (~line 211), add on a new line:

```
    The same one-pick lag applies to the channel's mood window
    (``channel.mood_low``/``mood_high``): a threshold change from the web UI
    can take effect one song late, because one pick is already buffered.
```

- [ ] **Step 6: Run the tests**

Run: `~/.virtualenvs/wickedjukebox/bin/pytest test/test_prefetcher.py test/test_random_new.py test/test_components.py -q`
Expected: **all pass** (24 in test_prefetcher: 12 old + 4 Task 1 + 8 new; plus the
random/component neighbors).

- [ ] **Step 7: Format + commit**

Run black+isort (same venv binaries) on: `wickedjukebox/core/smartfind.py wickedjukebox/model/db/library.py wickedjukebox/component/random.py test/test_prefetcher.py`. Re-run tests if anything reformatted.

```bash
git add wickedjukebox/core/smartfind.py wickedjukebox/model/db/library.py \
  wickedjukebox/component/random.py test/test_prefetcher.py
git commit --no-gpg-sign -m "feat: mood window filter in find_song + Song.random (NULL passes, never silent)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Best-effort mood filter in `AllFilesRandom` + full-suite verification

**Files:**
- Modify: `wickedjukebox/component/random.py` (imports ~lines 8-19; module constant;
  `AllFilesRandom.pick` ~lines 102-124)
- Create: `test/test_allfiles_mood.py`
- Test (regression): `test/test_random_new.py` must keep passing UNCHANGED — the existing
  `test_allfiles`/`test_allfiles_empty` patch only `Path`, so the DB probe must degrade
  gracefully when the global `Session` is unbound.

**Interfaces:**
- Consumes: `Channel.mood_range` (Task 1), `Song.by_filename` (existing; returns None and
  warns when the session has no bind).

- [ ] **Step 1: Write the failing tests**

Create `test/test_allfiles_mood.py`:

```python
# type: ignore
# pylint: skip-file
"""
AllFilesRandom mood filtering: a best-effort DB check per pick (see
docs/superpowers/specs/2026-07-11-mood-range-filter-design.md). Files live in
tmp_path; matching Song rows are seeded with localpath=str(p.absolute()) —
the same form the scanner writes. The module-level Session is patched to
hand out the test session.
"""

from contextlib import contextmanager
from typing import Any, Dict
from unittest.mock import patch

import wickedjukebox.component.random as rnd
from wickedjukebox.model.db.library import Song


@contextmanager
def _session_cm(dbsession):
    yield dbsession


def _picker(tmp_path):
    obj = rnd.AllFilesRandom(None, "test-channel")
    obj.root = str(tmp_path)
    return obj


def _seed_song(dbsession, default_data, path, mood_score):
    song = Song(localpath=str(path.absolute()))
    song.artist = default_data["default_artist"]
    song.album = default_data["default_album"]
    song.title = path.name
    song.duration = 300
    song.mood_score = mood_score
    dbsession.add(song)
    dbsession.flush()
    return song


def _window(dbsession, default_data, low, high):
    default_data["default_channel"].mood_low = low
    default_data["default_channel"].mood_high = high
    dbsession.flush()


def test_filter_off_picks_normally(
    tmp_path, dbsession, default_data: Dict[str, Any]
):
    """No mood window: behaves exactly like the classic picker."""
    (tmp_path / "a.mp3").write_bytes(b"")
    with patch.object(rnd, "Session", lambda: _session_cm(dbsession)):
        result = _picker(tmp_path).pick()
    assert result == str((tmp_path / "a.mp3").resolve())


def test_in_range_file_wins(
    tmp_path, dbsession, default_data: Dict[str, Any]
):
    """Out-of-range files are rejected in favour of an in-range one."""
    for index in range(5):
        out = tmp_path / f"out{index}.mp3"
        out.write_bytes(b"")
        _seed_song(dbsession, default_data, out, 95)
    (tmp_path / "in.mp3").write_bytes(b"")
    _seed_song(dbsession, default_data, tmp_path / "in.mp3", 50)
    _window(dbsession, default_data, 20, 80)
    with patch.object(rnd, "Session", lambda: _session_cm(dbsession)):
        result = _picker(tmp_path).pick()
    assert result == str((tmp_path / "in.mp3").resolve())


def test_unknown_file_passes(
    tmp_path, dbsession, default_data: Dict[str, Any]
):
    """A file the DB does not know about passes an active window."""
    (tmp_path / "unknown.mp3").write_bytes(b"")
    _window(dbsession, default_data, 20, 80)
    with patch.object(rnd, "Session", lambda: _session_cm(dbsession)):
        result = _picker(tmp_path).pick()
    assert result == str((tmp_path / "unknown.mp3").resolve())


def test_all_out_of_range_falls_back(
    tmp_path, dbsession, default_data: Dict[str, Any]
):
    """Every sampled file outside the window: still returns a pick."""
    (tmp_path / "x.mp3").write_bytes(b"")
    (tmp_path / "y.mp3").write_bytes(b"")
    _seed_song(dbsession, default_data, tmp_path / "x.mp3", 95)
    _seed_song(dbsession, default_data, tmp_path / "y.mp3", 96)
    _window(dbsession, default_data, 20, 80)
    with patch.object(rnd, "Session", lambda: _session_cm(dbsession)):
        result = _picker(tmp_path).pick()
    assert result in {
        str((tmp_path / "x.mp3").resolve()),
        str((tmp_path / "y.mp3").resolve()),
    }


def test_db_unavailable_falls_back(
    tmp_path, dbsession, default_data: Dict[str, Any]
):
    """The unbound global Session must degrade to an unfiltered pick."""
    (tmp_path / "a.mp3").write_bytes(b"")
    # Deliberately NOT patching rnd.Session: the module-global scoped
    # session has no bind in the test process, so the DB probe raises and
    # the picker must swallow it.
    result = _picker(tmp_path).pick()
    assert result == str((tmp_path / "a.mp3").resolve())
```

- [ ] **Step 2: Run to verify failure**

Run: `~/.virtualenvs/wickedjukebox/bin/pytest test/test_allfiles_mood.py -q`
Expected: `test_in_range_file_wins` FAILS (the classic picker ignores mood; with 5 of 6
files out of range it picks a wrong file with p≈83% per run — if it passes by luck, run it
again; at least one run must fail before implementing). The other tests may already pass
(they assert fallback behavior).

- [ ] **Step 3: Implement**

`wickedjukebox/component/random.py`:

1. Imports (~lines 8-19): replace `from random import choice` with
   `from random import sample`; extend the typing import with `List`
   (`from typing import Any, Dict, List, Mapping, Optional, Set`). The `Channel` import
   was added in Task 2.

2. After the module imports (below the last `from wickedjukebox...` import), add:

```python
#: How many glob candidates a single pick may probe against the mood window
#: before giving up and playing the first sample anyway (never silent).
MOOD_SAMPLE_SIZE = 50
```

3. Replace `AllFilesRandom.pick` (~lines 102-124) with these TWO methods:

```python
    def pick(self) -> str:
        if self.root == "":
            self._log.error(
                "%r has no 'root folder' configured. Cannot find files!", self
            )
            return ""
        pth = Path(self.root)
        candidates = list(pth.glob("**/*.mp3"))
        if not candidates:
            self._log.info(
                "Files configured using random in %r but no files "
                "found in that folder!",
                self.root,
            )
            return ""
        samples = sample(candidates, min(MOOD_SAMPLE_SIZE, len(candidates)))
        pick = self._apply_mood_filter(samples)
        output = str(pick.resolve())
        self._log.debug(
            "Picked %r as random file from all files in %r",
            output,
            pth.resolve(),
        )
        return output

    def _apply_mood_filter(self, samples: "List[Path]") -> Path:
        """
        Return the first sampled file inside the channel's mood window.

        Best-effort by design: files unknown to the DB and songs without a
        mood score always pass, an exhausted sample falls back to the first
        sample, and ANY database trouble degrades to an unfiltered pick —
        this picker must keep working without a DB (see the integration
        contract: never go silent). The window is read fresh on every pick.
        """
        try:
            with Session() as session:  # type: ignore
                mood_range = Channel.mood_range(session, self.channel_name)
                if mood_range is None:
                    return samples[0]
                low, high = mood_range
                for candidate in samples:
                    song = Song.by_filename(
                        session, str(candidate.absolute())
                    )
                    if (
                        song is None
                        or song.mood_score is None
                        or low <= song.mood_score <= high
                    ):
                        return candidate
                self._log.info(
                    "No sampled file inside mood range %r; picking "
                    "unfiltered",
                    mood_range,
                )
        except Exception:  # pylint: disable=broad-except
            self._log.warning(
                "Mood filter unavailable; picking unfiltered", exc_info=True
            )
        return samples[0]
```

- [ ] **Step 4: Run the new tests + regression neighbors**

Run: `~/.virtualenvs/wickedjukebox/bin/pytest test/test_allfiles_mood.py test/test_random_new.py -q`
Expected: all pass — including the UNCHANGED `test_allfiles`/`test_allfiles_empty`
(their mocked `Path` yields one candidate; the unbound global Session makes
`_apply_mood_filter` fall back).

- [ ] **Step 5: Full suite**

Run: `~/.virtualenvs/wickedjukebox/bin/pytest -q`
Expected: **107 passed** (90 baseline + 4 + 8 + 5 new), 0 failures.

- [ ] **Step 6: Format + commit**

black + isort on `wickedjukebox/component/random.py test/test_allfiles_mood.py`; re-run
the two test files if reformatted.

```bash
git add wickedjukebox/component/random.py test/test_allfiles_mood.py
git commit --no-gpg-sign -m "feat: best-effort mood window filter in AllFilesRandom

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Post-merge deploy (operator notes)

`pip install .` into the daemon's environment + restart the channel process(es). No config
change (prod stays `allfiles_random`, now mood-aware). Prod schema already has the columns
— do NOT run alembic against prod.
