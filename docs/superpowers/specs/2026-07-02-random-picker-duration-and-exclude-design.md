# Random Picker: Max-Duration Enforcement & Per-Song Exclude Flag

**Date:** 2026-07-02
**Status:** Approved (design)
**Scope:** `smart_prefetch` autoplay picker only

## Goal

Add two controls to the random/autoplay song selection used by the
`smart_prefetch` picker:

1. **Maximum track duration** — tracks longer than a configured number of
   seconds must never be selected by the random picker (e.g. skip anything
   over 10 minutes).
2. **Per-song exclude flag** — a boolean column on each song, a sibling to
   `broken`, that hard-excludes a song from being auto-picked at random while
   still allowing it to be played when explicitly queued or manually
   requested.

## Background / Current State

- The `smart_prefetch` picker (`component/random.py`) runs the scoring query in
  `core/smartfind.py:find_song`. That query **already** enforces a
  `max_duration` config value: both `smart_random_no_users` and
  `smart_random_with_users` filter `Song.duration < max_random_duration`, the
  key is declared in `SmartPrefetch.CONFIG_KEYS`, and it is documented in the
  `SmartPrefetch` docstring (`max_duration = 600`).
- `find_song` also already filters `not_(Song.broken)` (`smartfind.py:256`).
- Two gaps / defects exist around feature #1:
  - The `Song.duration < max_random_duration` filter line is **duplicated** in
    both query-builder functions (harmless, but incorrect).
  - The channel's **first song** after startup is fetched via
    `Song.random()` (`model/db/library.py:281`, called from
    `component/random.py:161`). That naive random ignores `max_duration`,
    `broken`, **and** any exclude flag — so an over-length, broken, or
    excluded song can still be picked as the very first track.
- `broken` is only ever *read* (filtered) in this codebase; nothing here writes
  it. It is set externally (direct DB / web UI). The new flag mirrors this: the
  application reads/filters it but does not provide a writer.

## Non-Goals (YAGNI)

- **`allfiles_random` picker** — pure filesystem globbing with no DB access; out
  of scope. Only `smart_prefetch` is covered.
- **No new config keys.** `max_duration` already exists; the exclude flag is a
  pure per-song DB column with no config.
- **No CLI / scanner writer** for the new flag. It is set externally, exactly
  like `broken`.
- **`max_duration` semantics unchanged** — it remains a required config key for
  `smart_prefetch` and an exclusive upper bound (`duration < max_duration`).

## Design

### Feature #2 — `exclude_from_random` column

**Model** (`model/db/library.py`, `Song`): add beside `broken`:

```python
exclude_from_random = Column(
    Boolean, nullable=False, server_default=text("0")
)
```

and a matching index in `Song.__table_args__`, mirroring the existing
`Index("broken", "broken", unique=False)`:

```python
Index("exclude_from_random", "exclude_from_random", unique=False),
```

**Design decision — `NOT NULL`:** unlike `broken` (which is nullable), this
column is defined `NOT NULL DEFAULT 0`. A nullable boolean is a latent footgun:
`not_(Song.exclude_from_random)` evaluates to `NULL` (falsy in a `WHERE`
clause) for a `NULL` value, which would silently exclude that song from random
selection — the opposite of the intended default. `NOT NULL DEFAULT 0`
guarantees every row participates unless explicitly flagged, and MariaDB
backfills existing rows to `0` when the column is added.

**Migration** (new file under `alembic/versions/`, `down_revision =
"b3d9f1a2c4e6"` — the current head):

- `upgrade`: `op.add_column("song", sa.Column("exclude_from_random",
  sa.Boolean(), nullable=False, server_default=sa.text("0")))` followed by
  `op.create_index("exclude_from_random", "song", ["exclude_from_random"],
  unique=False)`.
- `downgrade`: `op.drop_index` then `op.drop_column`.

**Filter** (`core/smartfind.py:find_song`): add one line beside the existing
broken filter (~line 256), so it applies to both the user-aware and no-user
query variants:

```python
query = query.filter(not_(Song.broken))
query = query.filter(not_(Song.exclude_from_random))   # new
```

### Feature #1 — `max_duration` gap closure

The scoring queries already enforce `max_duration`. Two changes complete it:

1. **De-duplicate the filter.** Remove the second, duplicated
   `query.filter(Song.duration < max_random_duration)` line in both
   `smart_random_no_users` and `smart_random_with_users`.

2. **Close the quick-prefetch gap.** Extend `Song.random()` to apply the same
   guards as the smart query, and pass `max_duration` through from the
   prefetch thread:

   ```python
   @staticmethod
   def random(session, max_duration=None):
       query = session.query(Song).filter(not_(Song.broken))
       query = query.filter(not_(Song.exclude_from_random))
       if max_duration is not None:
           query = query.filter(Song.duration < max_duration)
       return query.order_by(func.rand()).first()
   ```

   In `component/random.py` (~line 161), pass the configured max duration:
   `Song.random(session, self.scoring_config[ScoringConfig.MAX_DURATION])`.
   The `max_duration=None` default keeps the existing
   `test_prefetcher.py:33` call (`Song.random(dbsession)`) working unchanged
   and yields the previous "no duration filter" behaviour for any other
   caller.

`not_` and `func` are already imported in the respective modules
(`smartfind.py` imports `not_`; `library.py` imports `func`); `not_` must be
added to `library.py`'s imports for `Song.random`.

## Data Flow (after change)

1. Channel starts → `SmartPrefetchThread.run()` → `Song.random(session,
   max_duration)` returns a first song that is not broken, not excluded, and
   within the duration cap.
2. Steady state → `find_song()` scoring query returns candidates already
   filtered by `duration < max_duration`, `not broken`, and
   `not exclude_from_random`.
3. Explicit queueing (the `db` queue component) is unaffected — an
   `exclude_from_random` song can still be queued and played on request.

## Testing

Extend `test/test_prefetcher.py` (uses the `dbsession` / `default_data`
fixtures; songs are created in-session with an explicit `duration`):

- **Max duration, smart query:** add an over-length song
  (`duration > max_duration`), assert `find_song(...)` does not return it and
  returns an eligible song instead.
- **Max duration, quick prefetch:** assert `Song.random(session,
  max_duration)` never returns the over-length song.
- **Exclude flag, smart query:** add a song with `exclude_from_random=True`,
  assert `find_song(...)` does not return it.
- **Exclude flag, quick prefetch:** assert `Song.random(session)` does not
  return the excluded song.
- **Regression:** existing `test_random` / `test_smart_random` still pass
  (default song has `broken`/`exclude_from_random` defaulting to `0`, so it
  remains eligible).

Tests require a running MariaDB with migrations applied (per `conftest.py`),
so the new migration is exercised by the suite.

## Affected Files

- `wickedjukebox/model/db/library.py` — new column, index, `Song.random`
  signature/body, `not_` import.
- `wickedjukebox/core/smartfind.py` — new exclude filter line; remove duplicated
  duration filter in both builder functions.
- `wickedjukebox/component/random.py` — pass `max_duration` into
  `Song.random`.
- `alembic/versions/<new>_add_song_exclude_from_random.py` — new migration.
- `test/test_prefetcher.py` — new tests.
