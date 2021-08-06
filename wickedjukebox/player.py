import logging
from abc import ABC, abstractmethod
from math import floor
from pathlib import Path
from typing import Dict, List, NamedTuple

from mpd.base import MPDClient

from wickedjukebox.adt import Song
from wickedjukebox.logutil import qualname

MpdSong = Dict[str, str]


class PathMap(NamedTuple):
    """
    Maps a file-system path as known by the jukebox to a path known by mpd
    """

    jukebox_path: Path
    mpd_path: Path


class AbstractPlayer(ABC):
    def __init__(self) -> None:
        self.songs_since_last_jingle = 0
        self._log = logging.getLogger(qualname(self))

    def __repr__(self) -> str:
        return f"<{qualname(self)}>"

    @abstractmethod
    def skip(self) -> None:
        ...

    @abstractmethod
    def enqueue(self, song: Song, is_jingle: bool = False) -> None:
        ...

    @property
    @abstractmethod
    def remaining_seconds(self) -> int:
        ...

    @property
    @abstractmethod
    def upcoming_songs(self) -> List[Song]:
        ...


class NullPlayer(AbstractPlayer):
    def skip(self) -> None:
        self._log.debug("Skipping (no-op)")
        return

    def enqueue(self, song: Song, is_jingle: bool = False) -> None:
        self._log.debug("Queuing %r, jingle: %r (no-op)", song, is_jingle)
        return None

    @property
    def remaining_seconds(self) -> int:
        return 0

    @property
    def upcoming_songs(self) -> List[Song]:
        return []


class MpdPlayer(AbstractPlayer):
    def __init__(self, path_map: PathMap) -> None:
        super().__init__()
        self.client = None
        self.path_map = path_map

    def from_song(self, jukebox_item: Song) -> MpdSong:
        jukebox_root = str(self.path_map.jukebox_path)
        relative_name = jukebox_item.filename[len(jukebox_root) + 1 :]
        return {"file": relative_name}

    def to_song(self, mpd_item: MpdSong) -> Song:
        return Song(
            mpd_item["artist"],
            mpd_item["album"],
            mpd_item["title"],
            mpd_item["file"],
        )

    def connect(self) -> None:
        """
        Connect to MPD (if not yet connected)
        """
        if self.client is not None:
            return
        mpd_host = "127.0.0.1"
        mpd_port = 6600
        self._log.info("Connecting to MPD via %s:%s", mpd_host, mpd_port)
        client = MPDClient()
        client.timeout = 10
        client.idletimeout = None
        client.connect(mpd_host, mpd_port)  # type: ignore
        client.consume(1)  # type: ignore
        self.client = client

    def skip(self) -> None:
        self.connect()
        raise NotImplementedError()

    def enqueue(self, song: Song, is_jingle: bool) -> None:
        self.connect()
        mpd_info = self.from_song(song)
        self._log.debug("Queuing %r to mpd", mpd_info["file"])
        self.client.add(mpd_info["file"])  # type: ignore

    @property
    def remaining_seconds(self) -> int:
        self.connect()
        status: Dict[str, str] = self.client.status()  # type: ignore
        current_song = status.get("song")
        playlist: List[MpdSong] = self.client.playlistinfo()  # type: ignore
        remaining_playtime = 0.0
        if current_song is not None:
            current_playlist_pos = int(current_song)
            songinfo = playlist[current_playlist_pos]
            remaining_playtime = float(songinfo["duration"]) - float(
                status.get("elapsed", 0)
            )
            for row in playlist[current_playlist_pos + 1 :]:
                remaining_playtime += float(row["duration"])
        self._log.debug("Remaining playtime: %3.2f", remaining_playtime)
        return floor(remaining_playtime)

    @property
    def upcoming_songs(self) -> List[Song]:
        self.connect()
        current_playlist_pos = 0
        status: Dict[str, str] = self.client.status()  # type: ignore
        current_song = status.get("song")

        # If the player is stopped, the "current song" is technically "upcoming"
        # so we need to include it in the output. In other cases only the
        # following songs are "upcoming"
        if status.get("state") == "stop":
            offset = -1
        else:
            offset = 0
        if current_song is not None:
            current_playlist_pos = int(current_song)
        first_upcoming = current_playlist_pos + offset

        playlist: List[MpdSong] = self.client.playlistinfo()  # type: ignore
        output = [self.to_song(item) for item in playlist[first_upcoming:]]
        return output
