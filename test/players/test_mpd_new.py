"""
This module contains for the new (2021) MPD implementation
"""

from pathlib import Path
from typing import Tuple
from unittest.mock import Mock, patch

import pytest

import wickedjukebox.player as p
from wickedjukebox.adt import Song


@pytest.fixture
def mocked_player():
    with patch("wickedjukebox.player.MPDClient") as MPDClient:
        player = p.MpdPlayer(
            p.PathMap(Path("/jukebox/root"), Path("/mpd/root"))
        )
        yield player, MPDClient


def test_repr(mocked_player: Tuple[p.MpdPlayer, Mock]):
    result = repr(mocked_player[0])
    assert "MpdPlayer" in result


def test_null_player():
    player = p.NullPlayer()
    player.skip()
    player.enqueue(Song("", "", "", "foo"))
    assert player.remaining_seconds == 0
    assert player.upcoming_songs == []


def test_path_jukebox2mpd(mocked_player: Tuple[p.MpdPlayer, Mock]):
    player, _ = mocked_player
    result = player.jukebox2mpd("/jukebox/root/artist/album/track.mp3")
    expected = "artist/album/track.mp3"
    assert result == expected


def test_path_conversion_invariance(mocked_player: Tuple[p.MpdPlayer, Mock]):
    player, _ = mocked_player
    filename = "/jukebox/root/artist/album/track.mp3"
    result = player.mpd2jukebox(player.jukebox2mpd(filename))
    assert result == filename


def test_connect(mocked_player: Tuple[p.MpdPlayer, Mock]):
    player, MPDClient = mocked_player
    assert player.client is None
    sentinel = Mock()
    MPDClient.return_value = sentinel
    player.connect()
    player.connect()
    assert player.client is sentinel
    sentinel.connect.assert_called_once()  # type: ignore


def test_enqueue(mocked_player: Tuple[p.MpdPlayer, Mock]):
    player, MPDClient = mocked_player
    client = Mock()
    MPDClient.return_value = client
    player.enqueue(Song("", "", "", "/jukebox/root/foo.mp3"), is_jingle=False)
    client.add.assert_called_with("foo.mp3")  # type: ignore


def test_remaining_seconds(mocked_player: Tuple[p.MpdPlayer, Mock]):
    player, MPDClient = mocked_player
    client = Mock()
    MPDClient.return_value = client
    client.status.return_value = {  # type: ignore
        "song": "0",
        "elapsed": "10.0",
    }
    client.playlistinfo.return_value = [  # type: ignore
        {"file": "foo.mp3", "duration": "300.0"},
        {"file": "bar.mp3", "duration": "300.0"},
    ]

    result = player.remaining_seconds
    expected = 590
    assert result == expected


def test_upcoming_songs(mocked_player: Tuple[p.MpdPlayer, Mock]):
    player, MPDClient = mocked_player
    client = Mock()
    MPDClient.return_value = client
    client.status.return_value = {  # type: ignore
        "song": "0",
        "elapsed": "10.0",
    }
    client.playlistinfo.return_value = [  # type: ignore
        {"file": "foo.mp3", "duration": "300.0"},
        {"file": "bar.mp3", "duration": "300.0"},
    ]
    result = player.upcoming_songs
    expected = ["/jukebox/root/foo.mp3", "/jukebox/root/bar.mp3"]
    assert result == expected
