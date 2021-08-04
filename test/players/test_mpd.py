from typing import Optional, Tuple
from wickedjukebox.adt import Song
from wickedjukebox.demon.lib import mpdclient
from wickedjukebox.demon.players.mpd import Player
from datetime import datetime
from unittest.mock import Mock, patch
import pytest
import wickedjukebox.demon.players.common as common


@pytest.fixture
def mpd():
    with patch(
        "wickedjukebox.demon.players.mpd.mpdclient.MpdController"
    ) as ptch:
        yield ptch


@pytest.fixture
def connected_mpd(mpd):
    connection = Mock()
    mpd.return_value = connection
    player = Player(
        1, {"host": "192.0.2.1", "port": 123, "root_folder": "/path/to/mp3s"}
    )
    player.connect()
    yield player


def test_connect(mpd):
    player = Player(
        1, {"host": "192.0.2.1", "port": 123, "root_folder": "/path/to/mp3s"}
    )
    sentinel = object()
    mpd.return_value = sentinel
    player.connect()
    mpd.assert_called_with("192.0.2.1", 123)
    assert player.connection is sentinel


def test_connect_retry(mpd):
    player = Player(
        1, {"host": "192.0.2.1", "port": 123, "root_folder": "/path/to/mp3s"}
    )
    sentinel = object()
    mpd.return_value = sentinel
    player.connect()
    mpd.assert_called_with("192.0.2.1", 123)
    assert player.connection is sentinel


def test_disconnect(mpd):
    player = Player(
        1, {"host": "192.0.2.1", "port": 123, "root_folder": "/path/to/mp3s"}
    )
    player.connect()
    player.disconnect()
    assert player.connection is None


def test_connection_getter(mpd):
    player = Player(
        1, {"host": "192.0.2.1", "port": 123, "root_folder": "/path/to/mp3s"}
    )
    sentinel = object()
    mpd.return_value = sentinel
    player.connect()
    assert player.connection is sentinel


@pytest.mark.parametrize(
    "filename", ["filename.mp3", "/path/to/mp3s/filename.mp3"]
)
def test_queue(connected_mpd: Player, filename: str):
    status = Mock()
    status.playlistLength = 10
    status.song = 3
    connected_mpd.connection.getStatus.return_value = status
    connected_mpd.sys_utctime = 1
    with patch("wickedjukebox.demon.players.mpd.datetime") as dt:
        dt.now.return_value = datetime(2001, 1, 1)
        connected_mpd.connection.add.return_value = ["sentinel"]
        result = connected_mpd.queue(filename)
    connected_mpd.connection.add.assert_called_with([b"filename.mp3"])
    assert result is True
    assert connected_mpd.song_started == datetime(2001, 1, 1)


def test_queue_utc_time(connected_mpd: Player):
    status = Mock()
    status.playlistLength = 10
    status.song = 3
    connected_mpd.connection.getStatus.return_value = status
    with patch("wickedjukebox.demon.players.mpd.datetime") as dt:
        dt.utcnow.return_value = datetime(2001, 1, 1)
        connected_mpd.connection.add.return_value = ["sentinel"]
        result = connected_mpd.queue("filename.mp3")
    assert result is True
    assert connected_mpd.song_started == datetime(2001, 1, 1)


def test_queue_not_in_mp3(connected_mpd: Player):
    """
    If MPD does not know about a file, we should not crash out, but ignore the
    file.
    """
    status = Mock()
    status.playlistLength = 10
    status.song = 3
    connected_mpd.connection.getStatus.return_value = status
    with patch("wickedjukebox.demon.players.mpd.datetime") as dt:
        dt.now.return_value = datetime(2001, 1, 1)
        connected_mpd.connection.add.return_value = []
        result = connected_mpd.queue("filename.mp3")
    assert result is False


def test_queue_failed_in_mp3(connected_mpd: Player):
    """
    If MPD queuing fails, we should not crash out, but ignore the file.
    """
    status = Mock()
    status.playlistLength = 10
    status.song = 3
    connected_mpd.connection.getStatus.return_value = status
    with patch("wickedjukebox.demon.players.mpd.datetime") as dt:
        dt.now.return_value = datetime(2001, 1, 1)
        connected_mpd.connection.add.side_effect = Exception("kaboom")
        result = connected_mpd.queue("filename.mp3")
    assert result is False


def test_start_playback(connected_mpd: Player):
    connected_mpd.start()
    connected_mpd.connection.play.assert_called_with()


def test_pause_playback(connected_mpd: Player):
    connected_mpd.pause()
    connected_mpd.connection.pause.assert_called_with()


def test_skip_playback(connected_mpd: Player):
    connected_mpd.skip()
    connected_mpd.connection.next.assert_called_with()


def test_stop_playback(connected_mpd: Player):
    connected_mpd.stop()
    connected_mpd.connection.stop.assert_called_with()


def test_crop_playlist(connected_mpd: Player):
    status = Mock()
    status.playlistLength = 10
    status.song = 8
    connected_mpd.connection.getStatus.return_value = status
    connected_mpd.crop_playlist(5)
    connected_mpd.connection.delete.assert_called_with([(0, 7)])


def test_crop_playlist_not_needed(connected_mpd: Player):
    """
    If the current song is inside the range we *would* crop, we skip cropping.
    """
    status = Mock()
    status.playlistLength = 10
    status.song = 2
    connected_mpd.connection.getStatus.return_value = status
    connected_mpd.crop_playlist(5)
    assert connected_mpd.connection.delete.call_count == 0


def test_crop_playlist_short(connected_mpd: Player):
    """
    If the current MPD playlist length is smaller than the crop-size, we skip
    cropping
    """
    status = Mock()
    status.playlistLength = 4
    status.song = 2
    connected_mpd.connection.getStatus.return_value = status
    connected_mpd.crop_playlist(5)
    assert connected_mpd.connection.delete.call_count == 0


def test_current_song(connected_mpd: Player):
    current_song = Mock()
    current_song.path = b"something"
    connected_mpd.connection.getCurrentSong.return_value = current_song
    result = connected_mpd.current_song()
    assert result == "/path/to/mp3s/something"


def test_current_song_empty(connected_mpd: Player):
    connected_mpd.connection.getCurrentSong.return_value = False
    result = connected_mpd.current_song()
    assert result is None


@pytest.mark.parametrize(
    "msg",
    [
        "not done processing current command",
        "playlistLength not found",
        "problem parsing song info",
    ],
)
def test_current_song_failed(connected_mpd: Player, msg: str):
    """
    Some exceptions can be ignored (and retried)
    """
    current_song = Mock()
    current_song.path = b"something"
    connected_mpd.connection.getCurrentSong.side_effect = [
        mpdclient.MpdError(msg=msg, num="the-num"),
        current_song,
    ]
    with patch("wickedjukebox.demon.players.mpd.time"):
        result = connected_mpd.current_song()
    assert result == "/path/to/mp3s/something"


@pytest.mark.parametrize(
    "mpd_pos, expected_pos",
    [
        ((50, 100), 50.0),
        (None, 0.0),
    ],
)
def test_position(
    connected_mpd: Player,
    mpd_pos: Optional[Tuple[int, int]],
    expected_pos: float,
):
    connected_mpd.connection.getSongPosition.return_value = mpd_pos
    result = connected_mpd.position()
    assert result == expected_pos


def test_position_failed(connected_mpd: Player):
    connected_mpd.connection.getSongPosition.side_effect = mpdclient.MpdError(
        "not done processing current command"
    )
    result = connected_mpd.position()
    assert result == 0.0


@pytest.mark.parametrize(
    "internal_code, expected",
    [
        (1, common.STATUS_STOPPED),
        (2, common.STATUS_STARTED),
        (3, common.STATUS_PAUSED),
        (99, "unknown (99)"),
    ],
)
def test_status(connected_mpd: Player, internal_code: int, expected: str):
    status = Mock()
    status.state = internal_code
    connected_mpd.connection.getStatus.return_value = status
    result = connected_mpd.status()
    assert result == expected


@pytest.mark.parametrize(
    "side_effect",
    [
        [mpdclient.MpdStoredError("kaboom"), Mock(state=1)],
        [
            mpdclient.MpdError("not done processing current command"),
            Mock(state=1),
        ],
        [mpdclient.MpdError("playlistLength not found"), Mock(state=1)],
    ],
)
def test_status_errored(connected_mpd: Player, side_effect):
    connected_mpd.connection.getStatus.side_effect = side_effect
    with patch("wickedjukebox.demon.players.mpd.time"):
        result = connected_mpd.status()
    assert result == "stopped"


def test_upcoming_songs(connected_mpd: Player):
    connected_mpd.connection.status.return_value = Mock(song=0)
    connected_mpd.connection.playlist.return_value = [
        Mock(album="album-1", artist="artist-1", path="pth-1", title="title-1"),
        Mock(album="album-2", artist="artist-2", path="pth-2", title="title-2"),
        Mock(album="album-3", artist="artist-3", path="pth-3", title="title-3"),
    ]
    result = list(connected_mpd.upcoming_songs())
    expected = [
        Song(
            album="album-2",
            artist="artist-2",
            filename="pth-2",
            title="title-2",
        ),
        Song(
            album="album-3",
            artist="artist-3",
            filename="pth-3",
            title="title-3",
        ),
    ]
    assert result == expected


def test_playlistsize(connected_mpd: Player):
    connected_mpd.connection.getStatus.return_value = Mock(playlistLength=10)
    result = connected_mpd.playlistSize()
    assert result == 10


def test_clear_playlist(connected_mpd: Player):
    connected_mpd.connection.getStatus.return_value = Mock(
        playlistLength=10, song=8
    )
    connected_mpd.clearPlaylist()
    connected_mpd.connection.delete.assert_called_with([(0, 7)])


def test_update_playlist(connected_mpd: Player):
    connected_mpd.updatePlaylist()
    connected_mpd.connection.sendUpdateCommand.assert_called_with()
