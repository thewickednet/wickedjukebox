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


def test_in_range_file_wins(tmp_path, dbsession, default_data: Dict[str, Any]):
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


def test_unknown_file_passes(tmp_path, dbsession, default_data: Dict[str, Any]):
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
    """A DB failure must degrade to an unfiltered pick (never silent)."""
    (tmp_path / "a.mp3").write_bytes(b"")

    def _raise():
        raise RuntimeError("db down")

    with patch.object(rnd, "Session", _raise):
        result = _picker(tmp_path).pick()
    assert result == str((tmp_path / "a.mp3").resolve())
