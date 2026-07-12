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
    with (
        patch("wickedjukebox.model.db.library.MetaFactory") as factory,
        patch("wickedjukebox.model.db.library.Session", lambda: dbsession),
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
    drifted = _album(dbsession, artist, "Trust Us", tmp_path / "old-location")
    (new_dir / "one.mp3").write_bytes(b"")
    song = _scan(dbsession, new_dir / "one.mp3", "Motorpsycho", "Trust Us")
    assert song.album.id == drifted.id
    count = dbsession.query(Album).filter_by(name="Trust Us").count()
    assert count == 1  # no duplicate row


def test_unknown_album_created_with_dir_path(tmp_path, dbsession, default_data):
    """A genuinely new album is created with path = the file's directory."""
    fresh_dir = tmp_path / "New Artist" / "First Album"
    fresh_dir.mkdir(parents=True)
    (fresh_dir / "one.mp3").write_bytes(b"")
    song = _scan(dbsession, fresh_dir / "one.mp3", "New Artist", "First Album")
    assert song.album.path == str(fresh_dir)
    assert song.album.name == "First Album"


def test_by_path_hit_and_miss(tmp_path, dbsession, default_data):
    artist = _artist(dbsession, "Someone")
    album = _album(dbsession, artist, "Anything", tmp_path / "somewhere")
    assert Album.by_path(str(tmp_path / "somewhere"), dbsession).id == album.id
    assert Album.by_path(str(tmp_path / "elsewhere"), dbsession) is None


def test_by_artist_and_name_picks_lowest_id(tmp_path, dbsession, default_data):
    artist = _artist(dbsession, "Dup Artist")
    first = _album(dbsession, artist, "Dup", tmp_path / "d1")
    _album(dbsession, artist, "Dup", tmp_path / "d2")
    found = Album.by_artist_and_name(artist, "Dup", dbsession)
    assert found.id == first.id


def test_by_artist_and_name_unflushed_artist_is_none(dbsession, default_data):
    ghost = Artist("Ghost")  # never added/flushed: no id yet
    assert Album.by_artist_and_name(ghost, "Anything", dbsession) is None
