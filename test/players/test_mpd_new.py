"""
This module contains for the new (2021) MPD implementation
"""
# pylint: disable=redefined-outer-name

from typing import Tuple
from unittest.mock import Mock, patch

import pytest

import wickedjukebox.component.player as p


@pytest.fixture
def mocked_player():
    """
    Provide a player instance with a mocked interface to MPD.
    """
    with patch("wickedjukebox.component.player.MPDClient") as MPDClient:
        player = p.MpdPlayer(None, "")
        player.configure(
            {
                "host": "localhost",
                "port": "6600",
                "path_map": "test/data/local_path:/mpd/root",
            }
        )
        yield player, MPDClient


def test_repr(mocked_player: Tuple[p.MpdPlayer, Mock]):
    """
    Ensure that calling a "repr" of the instance does not crash
    """
    result = repr(mocked_player[0])
    assert "MpdPlayer" in result


def test_null_player():
    """
    Ensure that we have a working "null-object" for the player class.
    """
    player = p.NullPlayer(None, "")
    player.skip()
    player.enqueue("foo")
    assert player.remaining_seconds == 0
    assert player.is_playing is False
    assert player.is_empty is False


def test_path_jukebox2mpd(mocked_player: Tuple[p.MpdPlayer, Mock]):
    """
    Ensure that we correctly map filenames from the local file-system to
    filenames relative to the MPD internal DB.
    """
    player, _ = mocked_player
    result = player.jukebox2mpd("test/data/local_path/artist/album/track.mp3")
    expected = "artist/album/track.mp3"
    assert result == expected


def test_path_conversion_invariance(mocked_player: Tuple[p.MpdPlayer, Mock]):
    """
    Ensure that path-mapping "from" and "to" MPD is a proper inverse function
    """
    player, _ = mocked_player
    filename = "test/data/local_path/artist/album/track.mp3"
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
    assert player.songs_since_last_jingle == 0
    player.enqueue("test/data/local_path/foo.mp3", is_jingle=False)
    assert player.songs_since_last_jingle == 1
    client.add.assert_called_with("foo.mp3")  # type: ignore


def test_enqueue_jingle(mocked_player: Tuple[p.MpdPlayer, Mock]):
    player, MPDClient = mocked_player
    client = Mock()
    MPDClient.return_value = client
    player.enqueue("test/data/local_path/foo.mp3", is_jingle=False)
    assert player.songs_since_last_jingle == 1
    player.enqueue("test/data/local_path/foo.mp3", is_jingle=True)
    assert player.songs_since_last_jingle == 0
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


@pytest.mark.parametrize(
    "state_str, expected",
    [
        ("play", True),
        ("stop", False),
        ("pause", False),
    ],
)
def test_is_playing(
    mocked_player: Tuple[p.MpdPlayer, Mock], state_str: str, expected: bool
):
    player, MPDClient = mocked_player
    client = Mock()
    MPDClient.return_value = client
    client.status.return_value = {  # type: ignore
        "state": state_str,
    }
    result = player.is_playing
    assert result == expected


def test_is_empty(mocked_player: Tuple[p.MpdPlayer, Mock]):
    player, MPDClient = mocked_player
    client = Mock()
    MPDClient.return_value = client
    client.playlistinfo.return_value = []  # type: ignore
    assert player.is_empty is True
