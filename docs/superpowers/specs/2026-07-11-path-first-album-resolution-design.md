# Path-first album resolution in the scanner — design

**Date:** 2026-07-11
**Problem:** `Song.update_metadata` resolves albums by NAME ONLY
(`Album.by_name(...)` → `.one_or_none()`, `model/db/library.py:322`). `album.name` is
non-unique; prod has 67 cross-artist duplicate names (13× "Greatest Hits") and, since the
djukebox upload release-discriminator (2026-07-11), deliberate same-artist duplicates
(Weezer's self-titled releases). A rescan of imported trees therefore either raises
`MultipleResultsFound` (aborting the scan) or silently re-links songs to the wrong
same-named album. This is the parked fix referenced by
`djukebox/docs/deployment.md` and the upload-release-discriminator spec.

**Prod evidence (read-only, 2026-07-11):** `album.path` is UNIQUE + NOT NULL and populated
on all 5359 albums; **0 directories contain songs of more than one album** (one dir ≈ one
album holds); 27 albums have ≥1 song whose dirname ≠ `album.path` (historical drift /
vanished-dir top-ups) — these need the fallback.

## Design

`Song.update_metadata` (`model/db/library.py:322-329`) resolves the album in three steps:

1. **Path-first:** `Album.by_path(dirname(localpath))` — new staticmethod,
   `filter_by(path=path).one_or_none()` (safe: column is UNIQUE). The scanner writes
   exactly this value on create, so every scanner- or djukebox-created album hits here.
2. **Artist-scoped name fallback** (covers the 27 drifted albums): new
   `Album.by_artist_and_name(artist, name)` —
   `filter_by(artist_id=artist.id, name=name).order_by(Album.id).first()`; returns None
   immediately when `artist.id is None` (a brand-new unflushed Artist has no albums).
   `.first()` (not `.one_or_none()`) — never raises on duplicates, deterministic by id.
3. **Create** `Album(name, artist, dirname_)` — unchanged.

`Album.by_name` is replaced by these two finders; delete it if a repo-wide grep confirms
`update_metadata` is its only caller (tests included), otherwise leave it but fix its
`.one_or_none()` to `.first()`.

Both new finders keep the existing session convention (`session: Optional[TSession] = None`
→ `session or Session()`), matching `Artist.by_name`.

**Accepted limitations (documented in the finder docstrings):**
- The name fallback can still reuse the wrong same-artist same-name *release* for a
  brand-new directory (the daemon reads no MusicBrainz release id from tags). Strictly
  better than today: deterministic, artist-scoped, never crashes.
- Stale `album.path` is never rewritten by the scanner (no self-healing of the 27 drifted
  rows) — read-only resolution, no new write paths.

## Tests (MariaDB suite)

New `test/test_album_resolution.py`, driving `Song.update_metadata` with
`MetaFactory.create` patched (audiometa dict) and `wickedjukebox.model.db.library.Session`
patched to return `dbsession`; song files are tmp_path files (update_metadata `stat()`s
the file, so they must exist on disk):

- Same-name albums on TWO artists + a scan of a file in one of their dirs → path-first
  reuses the right one; no `MultipleResultsFound`.
- Same artist + same name as TWO existing rows with different paths (the state the
  djukebox upload importer creates for e.g. Weezer's self-titled releases) → a scan in
  either directory links to that directory's own album; the releases are never merged and
  nothing crashes (the Weezer case).
- Drifted album (row path ≠ file dir, same artist+name, path lookup misses) → the
  artist-scoped name fallback reuses it; no duplicate row is created. (This is the
  deliberate flip side of the "wrong release for a brand-new dir" limitation above: from
  (artist, name, unknown dir) alone the two cases are indistinguishable, and reuse is
  right for the 27 drifted albums that exist today, while new releases normally arrive
  through the djukebox importer with correct paths.)
- Fresh artist + fresh album → created with `path=dirname`.
- Direct finder tests: `by_path` hit/miss; `by_artist_and_name` picks lowest id among
  duplicates and returns None for an unflushed artist.

## Out of scope

- Rewriting/healing stale `album.path` values.
- Reading MusicBrainz release ids in `audiometa` (would make the fallback release-exact) —
  future work.
- Any djukebox-side change (its matching was fixed 2026-07-11).

## Conventions & deploy

Branch `fix/path-first-album-resolution` off `develop` (after the mood-range-filter branch
merges). black + isort at line length 80. Deploy: `pip install .` + restart; afterwards
`jukebox-admin rescan` of imported trees is safe again (remove the warning from
djukebox's `docs/deployment.md` in a separate djukebox commit once this is deployed).
