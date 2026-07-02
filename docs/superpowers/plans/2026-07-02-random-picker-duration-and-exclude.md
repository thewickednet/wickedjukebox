# Random Picker: Max-Duration & Exclude Flag — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce a maximum track duration on every random-selection path and add a per-song `exclude_from_random` flag (sibling to `broken`) that hard-excludes a song from the `smart_prefetch` autoplay picker while still allowing explicit queueing.

**Architecture:** Add a `NOT NULL DEFAULT 0` boolean column `exclude_from_random` to the `song` table (model + Alembic migration + index). Filter it in the `smart_prefetch` scoring query (`core/smartfind.py:find_song`) beside the existing `broken` filter, and close the first-song gap by teaching the naive `Song.random()` prefetch to honor `broken`, `exclude_from_random`, and an optional `max_duration`. Also remove an accidentally duplicated duration filter in the two scoring-query builders.

**Tech Stack:** Python 3.10, SQLAlchemy < 2.0, Alembic, MariaDB/MySQL, pytest.

## Global Constraints

- Python 3.10; **SQLAlchemy < 2.0** (no 2.0-only APIs).
- Formatting: **black** and **isort** (black profile), **line-length = 80**. Run `./env/bin/black` / `./env/bin/isort` before committing, or `pre-commit run --files <changed>`.
- Tests **require a running MariaDB with migrations applied**. `conftest.py` runs `alembic upgrade head` once per session and wraps each test in a rolled-back transaction (fixtures `dbsession`, `default_data`).
- New column is **`NOT NULL DEFAULT 0`** (intentionally stricter than the nullable `broken`, to avoid `NULL` being treated as falsy under `not_(...)`).
- Any new model module must be importable by Alembic autogenerate — not relevant here (no new module; `library.py` is already imported).
- Tools are invoked from the venv: `./env/bin/<tool>`.

---

### Task 1: Add the `exclude_from_random` column, index, and migration

**Files:**
- Modify: `wickedjukebox/model/db/library.py` (class `Song`: `__table_args__` ~183-202, columns ~226)
- Create: `alembic/versions/c7a1e9b4f2d3_add_song_exclude_from_random.py`
- Test: `test/test_prefetcher.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `Song.exclude_from_random` — a mapped `Boolean` column, `NOT NULL`, defaulting to `0` (falsy) for every row. A DB index named `exclude_from_random` on that column. Migration head becomes `c7a1e9b4f2d3` (down_revision `b3d9f1a2c4e6`).

- [ ] **Step 1: Write the failing test**

Add to the end of `test/test_prefetcher.py`:

```python
def test_exclude_from_random_defaults_to_false(
    dbsession: Session, default_data: Dict[str, Any]
):
    """
    A freshly-inserted song must default to NOT excluded (server_default 0),
    and the column must be non-nullable.
    """
    song = default_data["default_song"]
    dbsession.refresh(song)
    assert song.exclude_from_random is not None
    assert not song.exclude_from_random
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./env/bin/pytest test/test_prefetcher.py::test_exclude_from_random_defaults_to_false -v`
Expected: FAIL — `AttributeError: 'Song' object has no attribute 'exclude_from_random'` (column not yet defined).

- [ ] **Step 3: Add the column and index to the model**

In `wickedjukebox/model/db/library.py`, inside `Song.__table_args__`, add the index right after the existing `broken` index:

```python
        Index("broken", "broken", unique=False),
        Index("exclude_from_random", "exclude_from_random", unique=False),
```

Then add the column immediately after the `broken` column (`broken = Column(Boolean, server_default=text("0"))`):

```python
    broken = Column(Boolean, server_default=text("0"))
    exclude_from_random = Column(
        Boolean, nullable=False, server_default=text("0")
    )
```

- [ ] **Step 4: Create the Alembic migration**

Create `alembic/versions/c7a1e9b4f2d3_add_song_exclude_from_random.py` with exactly:

```python
# type: ignore
# pylint: skip-file
"""add song.exclude_from_random

Add a per-song boolean flag that hard-excludes a song from the random /
autoplay picker (sibling to ``broken``). Defined NOT NULL DEFAULT 0 so that
NULL is never treated as falsy by the ``not_(...)`` filter. Explicit
queueing is unaffected.

Revision ID: c7a1e9b4f2d3
Revises: b3d9f1a2c4e6
Create Date: 2026-07-02
"""

import sqlalchemy as sa

from alembic import op

revision = "c7a1e9b4f2d3"
down_revision = "b3d9f1a2c4e6"


def upgrade():
    op.add_column(
        "song",
        sa.Column(
            "exclude_from_random",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.create_index(
        "exclude_from_random",
        "song",
        ["exclude_from_random"],
        unique=False,
    )


def downgrade():
    op.drop_index("exclude_from_random", table_name="song")
    op.drop_column("song", "exclude_from_random")
```

- [ ] **Step 5: Apply the migration to the test database**

Run: `./env/bin/alembic upgrade head`
Expected: alembic reports running revision `c7a1e9b4f2d3`. (Prerequisite: DB container up and `alembic.ini` pointed at it — `fab run-db-container` if needed.)

- [ ] **Step 6: Verify migration up/down round-trips**

Run: `./env/bin/alembic downgrade -1 && ./env/bin/alembic upgrade head`
Expected: both commands succeed (drops then re-adds the column/index cleanly).

- [ ] **Step 7: Run the test to verify it passes**

Run: `./env/bin/pytest test/test_prefetcher.py::test_exclude_from_random_defaults_to_false -v`
Expected: PASS.

- [ ] **Step 8: Format and commit**

```bash
./env/bin/black wickedjukebox/model/db/library.py alembic/versions/c7a1e9b4f2d3_add_song_exclude_from_random.py test/test_prefetcher.py
./env/bin/isort wickedjukebox/model/db/library.py alembic/versions/c7a1e9b4f2d3_add_song_exclude_from_random.py test/test_prefetcher.py
git add wickedjukebox/model/db/library.py alembic/versions/c7a1e9b4f2d3_add_song_exclude_from_random.py test/test_prefetcher.py
git commit -m "feat: add song.exclude_from_random column + migration

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Filter `exclude_from_random` in the smart query; de-duplicate the duration filter

**Files:**
- Modify: `wickedjukebox/core/smartfind.py` (`smart_random_no_users` ~133-147, `smart_random_with_users` ~182-193, `find_song` ~256)
- Test: `test/test_prefetcher.py`

**Interfaces:**
- Consumes: `Song.exclude_from_random` (Task 1).
- Produces: `find_song(session, scoring_config, is_mysql)` — unchanged signature — now additionally excludes rows where `exclude_from_random` is true, on both the no-users and with-users code paths.

- [ ] **Step 1: Write the failing test**

Add to `test/test_prefetcher.py`:

```python
def test_find_song_skips_excluded(
    dbsession: Session, default_data: Dict[str, Any]
):
    """
    A song flagged exclude_from_random must never be returned by find_song.
    With the only song excluded, find_song must return None.
    """
    default_data["default_song"].exclude_from_random = True
    dbsession.flush()
    assert find_song(dbsession, SCORING_CONFIG, True) is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./env/bin/pytest test/test_prefetcher.py::test_find_song_skips_excluded -v`
Expected: FAIL — `find_song` still returns the default song (assert `is None` fails), because the exclude filter is not applied yet.

- [ ] **Step 3: Add the exclude filter in `find_song`**

In `wickedjukebox/core/smartfind.py`, find the line (~256):

```python
    query = query.filter(not_(Song.broken))  # type: ignore
```

Add the sibling filter directly beneath it:

```python
    query = query.filter(not_(Song.broken))  # type: ignore
    query = query.filter(not_(Song.exclude_from_random))  # type: ignore
```

(`not_` is already imported at the top of `smartfind.py`.)

- [ ] **Step 4: Run test to verify it passes**

Run: `./env/bin/pytest test/test_prefetcher.py::test_find_song_skips_excluded -v`
Expected: PASS.

- [ ] **Step 5: Add a guard test for max_duration on the smart path, then de-duplicate the filter**

This behavior already works; the test guards it while we remove the duplicated filter line. Add to `test/test_prefetcher.py`:

```python
def test_find_song_respects_max_duration(
    dbsession: Session, default_data: Dict[str, Any]
):
    """
    find_song must not return a song longer than MAX_DURATION. With the only
    song over the cap, find_song must return None.
    """
    default_data["default_song"].duration = 900  # > 600 (SCORING_CONFIG cap)
    dbsession.flush()
    assert find_song(dbsession, SCORING_CONFIG, True) is None
```

Run it — it should already PASS:
`./env/bin/pytest test/test_prefetcher.py::test_find_song_respects_max_duration -v`
Expected: PASS (filter already present).

Now remove the duplicated filter. In `smart_random_no_users`, the current code is:

```python
    query = query.filter(Song.duration < max_random_duration)
    query = query.filter(Song.duration < max_random_duration)
    query = query.order_by(text("score DESC"))  # type: ignore
```

Change it to a single filter:

```python
    query = query.filter(Song.duration < max_random_duration)
    query = query.order_by(text("score DESC"))  # type: ignore
```

In `smart_random_with_users`, the current code is:

```python
    query = query.filter(Song.duration < max_random_duration)
    query = query.filter(func.ifnull(hates_query.c.count, 0) == 0)
    query = query.filter(Song.duration < max_random_duration)
    query = query.order_by(text("score DESC"))  # type: ignore
```

Change it to remove the second duration filter (keep the hates filter):

```python
    query = query.filter(Song.duration < max_random_duration)
    query = query.filter(func.ifnull(hates_query.c.count, 0) == 0)
    query = query.order_by(text("score DESC"))  # type: ignore
```

- [ ] **Step 6: Re-run both new tests plus the existing smart-random tests**

Run: `./env/bin/pytest test/test_prefetcher.py -k "find_song or smart_random" -v`
Expected: PASS for `test_find_song_skips_excluded`, `test_find_song_respects_max_duration`, `test_smart_random`, `test_smart_random_with_users` (de-dup did not change behavior).

- [ ] **Step 7: Format and commit**

```bash
./env/bin/black wickedjukebox/core/smartfind.py test/test_prefetcher.py
./env/bin/isort wickedjukebox/core/smartfind.py test/test_prefetcher.py
git add wickedjukebox/core/smartfind.py test/test_prefetcher.py
git commit -m "feat: exclude_from_random filter in find_song; drop duplicate duration filter

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Close the quick-prefetch gap in `Song.random`

**Files:**
- Modify: `wickedjukebox/model/db/library.py` (imports ~25-41; `Song.random` ~280-287)
- Modify: `wickedjukebox/component/random.py` (`SmartPrefetchThread.run` ~161)
- Test: `test/test_prefetcher.py`

**Interfaces:**
- Consumes: `Song.exclude_from_random` (Task 1); `ScoringConfig.MAX_DURATION` (existing enum).
- Produces: `Song.random(session, max_duration=None)` — new optional second parameter. Returns a random `Song` that is **not** broken, **not** excluded, and (when `max_duration` is given) shorter than `max_duration` seconds; returns `None` if no song qualifies. Existing no-arg callers keep the previous "no duration filter" behavior.

- [ ] **Step 1: Write the failing tests**

Add to `test/test_prefetcher.py`:

```python
def test_random_skips_excluded(
    dbsession: Session, default_data: Dict[str, Any]
):
    """Song.random must not return an exclude_from_random song."""
    default_data["default_song"].exclude_from_random = True
    dbsession.flush()
    assert Song.random(dbsession) is None


def test_random_skips_broken(
    dbsession: Session, default_data: Dict[str, Any]
):
    """Song.random must not return a broken song."""
    default_data["default_song"].broken = True
    dbsession.flush()
    assert Song.random(dbsession) is None


def test_random_respects_max_duration(
    dbsession: Session, default_data: Dict[str, Any]
):
    """Song.random must not return a song longer than max_duration."""
    default_data["default_song"].duration = 900
    dbsession.flush()
    assert Song.random(dbsession, max_duration=600) is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `./env/bin/pytest test/test_prefetcher.py -k "test_random_skips or test_random_respects" -v`
Expected: FAIL — `test_random_skips_excluded` / `test_random_skips_broken` return the default song (assert `is None` fails); `test_random_respects_max_duration` fails with `TypeError` (unexpected `max_duration` argument).

- [ ] **Step 3: Add `not_` to the library imports**

In `wickedjukebox/model/db/library.py`, add `not_` to the `sqlalchemy` import block (keep it alphabetical / black-formatted):

```python
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Table,
    Text,
    func,
    not_,
    text,
)
```

- [ ] **Step 4: Rewrite `Song.random` to apply the guards**

Replace the existing method:

```python
    @staticmethod
    def random(session: TSession) -> Optional["Song"]:
        """
        Retrieve a song from the database using the local filename as key
        """
        query = session.query(Song).order_by(func.rand())
        song = query.first()
        return song
```

with:

```python
    @staticmethod
    def random(
        session: TSession, max_duration: Optional[int] = None
    ) -> Optional["Song"]:
        """
        Retrieve a random song eligible for autoplay.

        Songs flagged ``broken`` or ``exclude_from_random`` are never
        returned. When *max_duration* is given, songs longer than that many
        seconds are also excluded. Returns ``None`` if nothing qualifies.
        """
        query = session.query(Song)
        query = query.filter(not_(Song.broken))
        query = query.filter(not_(Song.exclude_from_random))
        if max_duration is not None:
            query = query.filter(Song.duration < max_duration)
        query = query.order_by(func.rand())
        return query.first()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `./env/bin/pytest test/test_prefetcher.py -k "test_random" -v`
Expected: PASS for `test_random_skips_excluded`, `test_random_skips_broken`, `test_random_respects_max_duration`, and the pre-existing `test_random` (default song has broken/exclude defaulting to 0, so it is still returned).

- [ ] **Step 6: Wire `max_duration` into the prefetch thread**

In `wickedjukebox/component/random.py`, in `SmartPrefetchThread.run` (~161), change:

```python
            song = Song.random(session)  # type: ignore
```

to:

```python
            song = Song.random(
                session,  # type: ignore
                self.scoring_config[ScoringConfig.MAX_DURATION],
            )
```

(`ScoringConfig` is already imported in `random.py`; `self.scoring_config` already carries `MAX_DURATION`.)

- [ ] **Step 7: Run the full test file to confirm nothing regressed**

Run: `./env/bin/pytest test/test_prefetcher.py -v`
Expected: all tests PASS.

- [ ] **Step 8: Format and commit**

```bash
./env/bin/black wickedjukebox/model/db/library.py wickedjukebox/component/random.py test/test_prefetcher.py
./env/bin/isort wickedjukebox/model/db/library.py wickedjukebox/component/random.py test/test_prefetcher.py
git add wickedjukebox/model/db/library.py wickedjukebox/component/random.py test/test_prefetcher.py
git commit -m "feat: Song.random honors broken/exclude_from_random/max_duration

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Full verification

**Files:** none (verification only).

- [ ] **Step 1: Run the whole suite**

Run: `fab test` (spins up a fresh DB container, applies migrations including `c7a1e9b4f2d3`, runs pytest).
Expected: all tests pass, including the new duration/exclude tests and the existing `test_random` / `test_smart_random*`.

- [ ] **Step 2: Run pre-commit across changed files**

Run: `./env/bin/pre-commit run --files wickedjukebox/model/db/library.py wickedjukebox/core/smartfind.py wickedjukebox/component/random.py alembic/versions/c7a1e9b4f2d3_add_song_exclude_from_random.py test/test_prefetcher.py`
Expected: black, isort, check-yaml, trailing-whitespace all pass.

- [ ] **Step 3: Confirm the migration is the single head**

Run: `./env/bin/alembic heads`
Expected: exactly one head — `c7a1e9b4f2d3`.

---

## Self-Review

**Spec coverage:**
- Feature #1 max_duration on smart path → guarded (Task 2, Step 5) + duplicate filter removed (Task 2). ✓
- Feature #1 quick-prefetch gap → `Song.random` guards + thread wiring (Task 3). ✓
- Feature #2 column `exclude_from_random` NOT NULL DEFAULT 0 + index + migration → Task 1. ✓
- Feature #2 filter in find_song (both user paths) → Task 2. ✓
- Feature #2 quick-prefetch also honors exclude → Task 3. ✓
- No config changes / no allfiles_random / no CLI writer → respected (nothing added). ✓
- Tests per spec's test plan → Tasks 1-3 cover column default, smart-path exclude & max_duration, quick-prefetch exclude/broken/max_duration; positive path relies on existing `test_random` / `test_smart_random`. ✓

**Placeholder scan:** No TBD/TODO; every code step shows full code; migration id and down_revision are concrete. ✓

**Type consistency:** `Song.random(session, max_duration=None)` defined in Task 3 and called with `(session, self.scoring_config[ScoringConfig.MAX_DURATION])` in the same task; `exclude_from_random` column name identical across model, migration, filters, and tests. ✓
