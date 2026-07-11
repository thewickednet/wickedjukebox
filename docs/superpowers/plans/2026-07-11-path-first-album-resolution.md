# Path-First Album Resolution Implementation Plan (wickedjukebox)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The scanner resolves albums by directory path first (UNIQUE `album.path`), with an
artist-scoped name fallback — rescans of imported trees stop crashing on duplicate album
names and stop merging different releases.

**Architecture:** Two new `Album` finders (`by_path`, `by_artist_and_name`) replace the
name-only `Album.by_name` in `Song.update_metadata`; `Album.by_name` is deleted (single
caller). No schema change.

**Tech Stack:** SQLAlchemy 1.4, pytest against the live MariaDB container.

**Spec:** `docs/superpowers/specs/2026-07-11-path-first-album-resolution-design.md`

## Global Constraints

- Repo: `/home/wickeddoc/workspace/private/wickedjukebox`, branch
  `fix/path-first-album-resolution` off `develop` (created in Setup below).
- Python/tools: `~/.virtualenvs/wickedjukebox/bin/{pytest,black,isort}`; tests need the
  live `jukeboxdb` MariaDB container (running; DSN configured in
  `.wicked/wickedjukebox/config.ini`). Run pytest from the repo root. If the DB is down,
  report BLOCKED.
- Line length 80 (pyproject); black + isort on all touched files INCLUDING tests.
- Resolution order is contract: (1) `Album.by_path(dirname)` — exact, UNIQUE column;
  (2) `Album.by_artist_and_name(artist, name)` — `.order_by(Album.id).first()`, never
  `.one_or_none()`, returns None for an unflushed artist (`artist.id is None`);
  (3) create `Album(name, artist, dirname_)`. The fallback REUSES drifted albums — it must
  NOT create a duplicate row when an artist-scoped name match exists.
- Commits: `git commit --no-gpg-sign`, conventional prefix, trailer
  `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`. Never push.
- Suite baseline at branch time: 107 passed (after the mood-range-filter feature). One new
  test file adds 7 → **114 expected**.

**Setup (before Task 1):** from `develop`:
`git checkout -b fix/path-first-album-resolution`.

---

### Task 1: `Album.by_path` + `Album.by_artist_and_name`, rewire `update_metadata`, drop `by_name`

**Files:**
- Modify: `wickedjukebox/model/db/library.py` (Album finders ~lines 173-181; the
  `Album.by_name` call inside `Song.update_metadata` ~line 345)
- Create: `test/test_album_resolution.py`

**Interfaces:**
- Consumes: existing `Album(name, artist, path)` constructor, `Artist.by_name`,
  `Song.update_metadata`, conftest fixtures `dbsession`/`default_data`.
- Produces: `Album.by_path(path, session=None) -> Optional[Album]`;
  `Album.by_artist_and_name(artist, name, session=None) -> Optional[Album]`.
  `Album.by_name` no longer exists.

- [ ] **Step 1: Confirm `Album.by_name` has no other callers**

Run: `grep -rn "by_name" wickedjukebox/ test/ --include=*.py | grep -i album`
Expected: exactly one hit — `wickedjukebox/model/db/library.py` inside `update_metadata`
(`album = Album.by_name(audiometa["album"])`). If ANY other caller appears, STOP and
report BLOCKED with the hits (the deletion below would break them).

- [ ] **Step 2: Write the failing tests**

Create `test/test_album_resolution.py`:

```python
# type: ignore
# pylint: skip-file
"""
Path-first album resolution in Song.update_metadata (see
docs/superpowers/specs/2026-07-11-path-first-album-resolution-design.md).
Album directories are resolved by the UNIQUE album.path first; an
artist-scoped name fallback reuses drifted albums; only then is a new album
created. update_metadata stat()s the file, so every scanned path is a real
tmp file; MetaFactory and the module-level Session are patched.
"""

from unittest.mock import patch

from wickedjukebox.model.db.library import Album, Artist, Song


def _audiometa(artist_name, album_name):
    return {
        "artist": artist_name,
        "album": album_name,
        "genres": None,
        "title": "a title",
        "duration": 300,
        "bitrate": 192,
        "track_no": 1,
        "release_date": None,
    }


def _scan(dbsession, path, artist_name, album_name):
    """Run update_metadata for a (real) file with patched tag metadata."""
    song = Song(localpath=str(path))
    with patch(
        "wickedjukebox.model.db.library.MetaFactory"
    ) as factory, patch(
        "wickedjukebox.model.db.library.Session", lambda: dbsession
    ):
        factory.create.return_value = _audiometa(artist_name, album_name)
        song.update_metadata()
    dbsession.add(song)
    dbsession.flush()
    return song


def _album(dbsession, artist, name, path):
    album = Album(name, artist, str(path))
    dbsession.add(album)
    dbsession.flush()
    return album


def _artist(dbsession, name):
    artist = Artist(name)
    dbsession.add(artist)
    dbsession.flush()
    return artist


def test_cross_artist_same_name_resolves_by_path(
    tmp_path, dbsession, default_data
):
    """Duplicate album names on different artists must not crash or merge."""
    artist_a = _artist(dbsession, "Artist A")
    artist_b = _artist(dbsession, "Artist B")
    dir_a = tmp_path / "a" / "Greatest Hits"
    dir_b = tmp_path / "b" / "Greatest Hits"
    dir_a.mkdir(parents=True)
    dir_b.mkdir(parents=True)
    album_a = _album(dbsession, artist_a, "Greatest Hits", dir_a)
    _album(dbsession, artist_b, "Greatest Hits", dir_b)
    (dir_a / "song.mp3").write_bytes(b"")
    song = _scan(dbsession, dir_a / "song.mp3", "Artist A", "Greatest Hits")
    assert song.album.id == album_a.id


def test_same_artist_two_releases_never_merge(
    tmp_path, dbsession, default_data
):
    """The Weezer case: same artist+name rows with distinct paths (as the
    djukebox importer creates them) each keep their own directory."""
    weezer = _artist(dbsession, "Weezer")
    dir_1994 = tmp_path / "Weezer" / "1994 - Weezer"
    dir_2001 = tmp_path / "Weezer" / "2001 - Weezer"
    dir_1994.mkdir(parents=True)
    dir_2001.mkdir(parents=True)
    blue = _album(dbsession, weezer, "Weezer", dir_1994)
    green = _album(dbsession, weezer, "Weezer", dir_2001)
    (dir_2001 / "island.mp3").write_bytes(b"")
    song = _scan(dbsession, dir_2001 / "island.mp3", "Weezer", "Weezer")
    assert song.album.id == green.id
    assert song.album.id != blue.id


def test_drifted_album_reused_via_name_fallback(
    tmp_path, dbsession, default_data
):
    """Stale album.path (dir moved): the artist-scoped fallback reuses the
    row instead of duplicating it."""
    artist = _artist(dbsession, "Motorpsycho")
    new_dir = tmp_path / "Motorpsycho" / "Trust Us"
    new_dir.mkdir(parents=True)
    drifted = _album(
        dbsession, artist, "Trust Us", tmp_path / "old-location"
    )
    (new_dir / "one.mp3").write_bytes(b"")
    song = _scan(dbsession, new_dir / "one.mp3", "Motorpsycho", "Trust Us")
    assert song.album.id == drifted.id
    count = (
        dbsession.query(Album).filter_by(name="Trust Us").count()
    )
    assert count == 1  # no duplicate row


def test_unknown_album_created_with_dir_path(
    tmp_path, dbsession, default_data
):
    """A genuinely new album is created with path = the file's directory."""
    fresh_dir = tmp_path / "New Artist" / "First Album"
    fresh_dir.mkdir(parents=True)
    (fresh_dir / "one.mp3").write_bytes(b"")
    song = _scan(
        dbsession, fresh_dir / "one.mp3", "New Artist", "First Album"
    )
    assert song.album.path == str(fresh_dir)
    assert song.album.name == "First Album"


def test_by_path_hit_and_miss(tmp_path, dbsession, default_data):
    artist = _artist(dbsession, "Someone")
    album = _album(dbsession, artist, "Anything", tmp_path / "somewhere")
    assert (
        Album.by_path(str(tmp_path / "somewhere"), dbsession).id == album.id
    )
    assert Album.by_path(str(tmp_path / "elsewhere"), dbsession) is None


def test_by_artist_and_name_picks_lowest_id(
    tmp_path, dbsession, default_data
):
    artist = _artist(dbsession, "Dup Artist")
    first = _album(dbsession, artist, "Dup", tmp_path / "d1")
    _album(dbsession, artist, "Dup", tmp_path / "d2")
    found = Album.by_artist_and_name(artist, "Dup", dbsession)
    assert found.id == first.id


def test_by_artist_and_name_unflushed_artist_is_none(
    dbsession, default_data
):
    ghost = Artist("Ghost")  # never added/flushed: no id yet
    assert Album.by_artist_and_name(ghost, "Anything", dbsession) is None
```

- [ ] **Step 3: Run to verify failure**

Run: `~/.virtualenvs/wickedjukebox/bin/pytest test/test_album_resolution.py -q`
Expected: FAILURES/ERRORS — `test_cross_artist_same_name_resolves_by_path` and
`test_same_artist_two_releases_never_merge` raise `MultipleResultsFound` (today's
name-only `.one_or_none()`); the finder tests error with
`AttributeError: ... has no attribute 'by_path'`.

- [ ] **Step 4: Implement**

`wickedjukebox/model/db/library.py` — replace the whole `Album.by_name` staticmethod
(~lines 173-181) with these two finders:

```python
    @staticmethod
    def by_path(
        path: str, session: Optional[TSession] = None
    ) -> Optional["Album"]:
        """
        Resolve an album by its directory path (UNIQUE column).

        This is the primary scanner lookup: one directory is one album, and
        the scanner writes ``path = dirname(localpath)`` on creation, so
        every well-formed tree resolves here — including same-named albums
        (different artists, or different releases by the same artist).
        """
        session = session or Session()
        return session.query(Album).filter_by(path=path).one_or_none()

    @staticmethod
    def by_artist_and_name(
        artist: "Artist", name: str, session: Optional[TSession] = None
    ) -> Optional["Album"]:
        """
        Artist-scoped name fallback for directories the DB does not know
        (an album whose ``path`` drifted, e.g. after a move on disk).

        Album names are not unique — not even per artist — so this picks
        the lowest id deterministically instead of raising. Known
        limitation: for a genuinely NEW directory holding a same-named
        release by the same artist this reuses the older release; new
        releases normally arrive through the djukebox importer, which
        creates correctly-pathed rows that ``by_path`` then resolves.
        Returns None for an unflushed artist (it cannot own albums yet).
        """
        if artist.id is None:
            return None
        session = session or Session()
        return (
            session.query(Album)
            .filter_by(artist_id=artist.id, name=name)
            .order_by(Album.id)
            .first()
        )
```

In `Song.update_metadata` (~line 345), replace:

```python
        album = Album.by_name(audiometa["album"])
        if not album:
            album = Album(
                audiometa["album"],
                artist,
                dirname_,
            )
        self.album = album
```

with:

```python
        album = Album.by_path(dirname_)
        if album is None:
            album = Album.by_artist_and_name(artist, audiometa["album"])
        if album is None:
            album = Album(
                audiometa["album"],
                artist,
                dirname_,
            )
        self.album = album
```

- [ ] **Step 5: Run the new tests + neighbors**

Run: `~/.virtualenvs/wickedjukebox/bin/pytest test/test_album_resolution.py test/test_scanner.py test/test_prefetcher.py -q`
Expected: all pass (7 new + 5 scanner + 22 prefetcher = 34).

- [ ] **Step 6: Full suite**

Run: `~/.virtualenvs/wickedjukebox/bin/pytest -q`
Expected: **114 passed** (107 baseline + 7 new).

- [ ] **Step 7: Format + commit**

black + isort (venv binaries) on `wickedjukebox/model/db/library.py
test/test_album_resolution.py`; re-run Step 5 if reformatted.

```bash
git add wickedjukebox/model/db/library.py test/test_album_resolution.py
git commit --no-gpg-sign -m "fix: scanner resolves albums path-first with artist-scoped name fallback

Album.by_name (name-only, one_or_none) crashed on duplicate album names and
merged different releases; album.path is UNIQUE and written on creation, so
resolve by directory first, fall back to an artist-scoped .first() for
drifted paths, and only then create.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Post-merge deploy (operator notes)

`pip install .` + daemon restart (can ride along with the mood-range-filter deploy).
Afterwards `jukebox-admin rescan` of djukebox-imported trees is safe; the djukebox repo's
`docs/deployment.md` rescan warning should then be softened (separate djukebox commit).
