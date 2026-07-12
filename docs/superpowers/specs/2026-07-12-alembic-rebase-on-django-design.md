# Rebase the daemon's alembic/SQLAlchemy schema onto Django (functional reconciliation)

**Date:** 2026-07-12
**Status:** Approved (design)
**Repos:** `wickedjukebox` (this repo — the player daemon) ⇄ `djukebox` (sibling — the Django web UI/API)

## Problem

`djukebox` (Django) now owns the production database schema. `wickedjukebox`'s
SQLAlchemy models + Alembic migrations describe the *same* shared schema
independently, and the two have **drifted**. Concrete drift found on the `song`
table: the daemon declares a phantom single-column `exclude_from_random` index
that production does not have, and lacks the composite `song_avail_broken_idx
(available, broken)` index that production *does* have. This means the daemon's
tests run against a schema that no longer matches production.

## Key fact: the daemon's Alembic is dev/test-only

`wickedjukebox`'s Alembic **never runs against production**. It exists solely to
build ephemeral dev/test databases so the daemon's SQLAlchemy models have tables
to query:

- `fabfile.py` and `test/conftest.py` run `alembic upgrade head` to build throwaway DBs.
- CI (`.github/workflows/ci.yaml`) does the same before `pytest`.
- The migrations say so explicitly (`e8f2a4c6d0b1`: *"this migration only serves
  alembic-built dev/test databases"*; the mood-range plan: *"do NOT run alembic
  against prod"*).

Production DDL is applied exclusively by djukebox's Django migrations. So
"rebase alembic on Django" means: **make the daemon's alembic-built dev/test
schema a faithful mirror of Django's authoritative schema for the tables the
daemon uses**, eliminating drift so the daemon's tests exercise a
production-accurate schema.

## Decisions (locked during brainstorming)

1. **Scope:** daemon-used functional tables only (not the vestigial `auth_*` /
   `django_*` / infra tables the daemon also happens to declare).
2. **Chain strategy:** squash the 5-migration chain into a single clean baseline.
3. **Fidelity:** **functional reconciliation** — align indexes & column presence
   to Django where safe and meaningful; keep daemon-required constraints Django
   under-declares; do not chase cosmetic type/nullability churn. Verified by the
   daemon test suite.
4. **Tier 3 structural divergences** (surrogate-vs-composite PKs, Django-only
   columns/FKs) are **left as-is** and documented as intentional daemon-side
   deviations.

### Why not strict byte-parity to Django's fresh-migrate output

Django's **models/migrate-output are a lossy, partially-divergent description**
of the real schema. Matching them byte-for-byte would actively harm the daemon
(evidence from a real `manage.py migrate` dump of the `song` table):

| aspect | daemon (alembic) | Django fresh-migrate | matching Django would… |
|---|---|---|---|
| `id` PK | `int(11)` AUTO_INCREMENT | `int(10) unsigned`, no auto-increment | break fixtures that insert rows without ids |
| `localpath` | **UNIQUE** | *no unique* | drop a constraint `by_filename`/scanner depend on |
| `title`,`duration`,`bitrate`,… | nullable | NOT NULL | break fixtures creating partial rows |
| types | `datetime`,`float`,`varchar(32)` | `datetime(6)`,`double`,`uuid`,unsigned+`CHECK` | pervasive rewrite, no daemon benefit |

Django under-declares what the daemon needs (localpath uniqueness,
auto-increment ids) and over-tightens things that would break the daemon's
tests — the classic Django-state ≠ production gap that djukebox's own CLAUDE.md
warns about (it uses state-only migrations precisely because model state does
not match production). Functional reconciliation captures the *meaningful* drift
(indexes, column presence) without the harmful churn.

## Scope

### In-scope daemon tables
`song, artist, album, genre, tag, song_has_genre, song_has_tag, country,
collection, collection_has_song, channel, channel_song_data, channel_album_data,
state, queue, dynamicPlaylist, user_song_standing, user_song_stats,
user_album_stats, users, groups, setting, setting_text, playlist,
playlist_has_song`.

### Explicitly out of scope
- **Vestigial infra tables** the daemon declares but never queries: `auth_*`,
  `django_*`, `django_celery_results_*`, `rest_framework_tracking_apirequestlog`,
  `thumbnail_kvstore`, `render_presets`, `shoutbox`. The squashed baseline still
  **creates** them (so nothing breaks and FK closure holds) but they receive no
  reconciliation work.
- **`randomSongsToUse`** — legacy daemon table with no Django counterpart; left
  as-is.
- **Django-only tables** the daemon never uses: `cf_*` (recommender), `url`,
  `emote`, `channel_membership`, `playlist_membership`, `artist_fanart`,
  `artist_similarity`, `genre_group*`, `history`, `music_upload`,
  `token_blacklist_*`. Not added.

## Reconciliation plan (derived from a live schema diff)

### Tier 1 — the real win: `song` indexes
This is the drift behind the original slow-query investigation.
- **DROP** single-column indexes `broken`, `title`, `exclude_from_random`
  (Django has none; all low-cardinality / unused by the picker).
- **ADD** composite `song_avail_broken_idx (available, broken)` (production has it).
- **KEEP** `UNIQUE(localpath)`, `song_mood_score_idx (mood_score)`, `KEY(artist_id)`,
  `KEY(album_id)`, `UNIQUE(slug)`, `UNIQUE(intro_id)`, and the two FKs
  (column sets already match Django; keep the daemon's constraint names).

### Tier 2 — minor index cleanup toward Django (low risk)
- **DROP** daemon-only indexes Django lacks and the daemon does not use:
  - `album`: `KEY(name)` (declared twice — `__table_args__` *and* `index=True`), `KEY(type)`
  - `queue`: `KEY(position)`
  - `setting`: single `KEY(var)` (already covered by the leftmost of the
    `(var, channel_id, user_id)` composite unique)
  - `channel_song_data`: redundant single `KEY(channel_id)` (covered by the
    leftmost of the `(channel_id, song_id)` composite unique)
- **KEEP** daemon-needed uniques Django omits: `artist UNIQUE(name)`
  (`Artist.by_name` uses `.one_or_none()`), `album UNIQUE(path)`
  (`Album.by_path` uses `.one_or_none()`). These are keeps — no edit.
- **NOT added in this pass:** Django's parity FK indexes `channel.owner_id` and
  `users.channel_id` are not daemon-used; deferred as possible future parity to
  keep this change minimal and index-focused.

### Tier 3 — structural divergences deliberately left as-is (documented)
Reconciling these would break the daemon's fixtures/inserts for no functional
benefit, so the daemon keeps its current working structure:
- **Surrogate-vs-natural/composite PKs:** `tag` (Django PK = `label`),
  `user_song_stats` (daemon composite `(user_id, song_id, when)` vs Django
  surrogate `id`), `collection_has_song`, `playlist`, `playlist_has_song`.
- **Genre/tag join tables** (`song_has_genre`, `song_has_tag`) have minor
  index/FK differences tied to the `tag` PK divergence; not in the autoplay hot
  path — left as-is.
- **Django-only columns/FKs outside the daemon's world:**
  `playlist_has_song.added_by_id`; `users.django_user_id → auth_user`
  (auth_user is out of scope). Not added.

## Intentional daemon-side deviations (keep-list, to be documented in code)
These are places the daemon deliberately declares **more** than Django's model,
because the daemon relies on them and/or its tests do:
- `song.UNIQUE(localpath)`, `artist.UNIQUE(name)`, `album.UNIQUE(path)` — used by
  `by_filename` / `by_name` / `by_path` finders (`.one_or_none()` requires them).
- `AUTO_INCREMENT` integer PKs on `song`/`artist`/`album`/etc. — Django uses
  non-autoincrement `PositiveIntegerField` PKs; the daemon keeps auto-increment
  so fixtures and the scanner can insert without assigning ids.
- Tier 3 PK structures (above).

A short comment block in the models will record this keep-list so a future reader
does not "fix" it back toward Django and reintroduce the breakage.

## Squash mechanics
- Replace the 5 files in `alembic/versions/`
  (`7c6b18d72ff3` → `318551dda932` → `b3d9f1a2c4e6` → `c7a1e9b4f2d3` →
  `e8f2a4c6d0b1`) with **one** baseline migration that builds the reconciled
  `Base.metadata` (`down_revision = None`).
- Draft it via `alembic revision --autogenerate` against an empty DB, then
  hand-fix: `server_default`s, explicit index/constraint names, and FK
  `ondelete`/`onupdate` actions (autogenerate does not capture these reliably).
- Because dev/test DBs are ephemeral, the only fallout is "drop & recreate your
  local dev DB" — documented in the migration docstring and (if present) the dev
  setup notes.

## Files touched
Only tables with an actual Tier 1/Tier 2 index edit are listed. Tier 3 tables
(`tag`, `song_has_genre`, `song_has_tag`, `user_song_stats`, `user_album_stats`,
`channel_album_data`, `collection_has_song`, `playlist`, `playlist_has_song`) and
the keep-list tables (`artist`) are **not** modified.

- `wickedjukebox/model/db/library.py` — `song` (drop `broken`/`title`/
  `exclude_from_random` indexes, add `song_avail_broken_idx`); `album` (drop the
  duplicate `name` indexes and `type` index; keep `UNIQUE(path)`).
- `wickedjukebox/model/db/stats.py` — `channel_song_data` (drop the redundant
  single `channel_id` index).
- `wickedjukebox/model/db/playback.py` — `queue` (drop `position` index).
- `wickedjukebox/model/db/settings.py` — `setting` (drop the standalone `var`
  index; the `(var, channel_id, user_id)` composite covers it).
- `alembic/versions/` — delete the 5 existing migrations, add 1 squashed baseline.
- A comment block (in `library.py` near `song`) documenting the intentional
  deviations (keep-list).

Changes are **schema-only**: no edits to `Song.random`, `core/smartfind.py`, or
any query/behavior. The daemon's runtime logic is untouched.

## Verification
1. `alembic upgrade head` on a fresh MariaDB builds cleanly from the single baseline.
2. **Full daemon `pytest` suite green** — the primary oracle. The reconciliation
   is schema-only and behavior-preserving, so no test should regress. (Confirm no
   test asserts the existence of a dropped index; if one does, update it.)
3. **Reproducible drift check** (capture as a short doc/script so it can be re-run):
   - Spin up MariaDB and `alembic upgrade head` → `db A`.
   - Run djukebox `manage.py migrate` against a fresh DB → `db B`, then
     `mariadb-dump --no-data` both and diff the in-scope tables' index sets.
   - The diff should show **only** the intentional deviations (the keep-list) and
     the Tier 3 structural divergences — nothing else.

### Ground-truth derivation recipe (reproducibility notes)
- djukebox's venv (`~/.virtualenvs/djukebox`) has `mysqlclient`, so Django can
  migrate against MySQL.
- **MariaDB version gotcha:** djukebox migration `0030_cf_recommender` uses a
  `VECTOR` column (needs MariaDB **11.7+**). On MariaDB 10.x, fake just that one
  migration (`migrate music 0030 --fake`, then continue) — the `cf_*` tables are
  out of scope, and the later song-index migrations (`0032`, `0037`, `0042`) still
  apply. Alternatively run the derivation on MariaDB 11.7+.
- Point Django at MySQL with a throwaway settings module that does
  `from djukebox.settings_test import *` (inherits the no-external-services
  neutralization) then overrides `DATABASES["default"]` to the MySQL DSN.

## Non-goals
- No query/behavior changes to the daemon (that is a separate effort — see the
  slow-`ORDER BY RAND()` findings).
- No production DDL changes (Django owns production).
- No reconciliation of vestigial infra tables or Tier 3 structures.
- No attempt to make the daemon's schema match the *legacy production* schema
  byte-for-byte (only functional parity with Django, plus the keep-list).

## Risks & mitigations
- **A test asserts a dropped index** → surface during the pytest run; update the
  test. (Current tests assert columns/behavior, not index existence, so unlikely.)
- **Autogenerate misses server-defaults / FK actions** → hand-fix the baseline and
  verify with the drift check (step 3) before considering it done.
- **Future re-drift** → the reproducible drift check (step 3) is the guardrail;
  run it whenever either side changes the schema.
