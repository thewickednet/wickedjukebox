"""
This module contains implementations for the underlying player backends
"""
import logging
from abc import ABC, abstractmethod
from math import floor
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Set

from mpd.base import (  # type: ignore
    CommandError,
    FailureResponseCode,
    MPDClient,
)

from wickedjukebox.config import Config
from wickedjukebox.exc import ConfigError
from wickedjukebox.logutil import qualname, qualname_repr

MpdSong = Dict[str, str]


class PathMap(NamedTuple):
    """
    Maps a file-system path as known by the jukebox to a path known by mpd
    """

    jukebox_path: Path
    mpd_path: Path


@qualname_repr
class AbstractPlayer(ABC):
    """
    This class provides the interface for the underlying implementations
    """

    #: The names of the config-keys that this instance requires to be
    #: successfully configured.
    CONFIG_KEYS: Set[str] = set()

    def __init__(self, config: Optional[Config]) -> None:
        self.songs_since_last_jingle = 0
        self._log = logging.getLogger(qualname(self))
        self._config = config or Config()

    @abstractmethod
    def configure(self, cfg: Dict[str, Any]) -> None:
        """
        Process configuration data from a configuration mapping. The
        required keys depend on the specific player type.
        """
        # TODO: This can be implemented in the top-class (i.e. here) by defining
        #       the expected keys as a class-variable and then "pulling them in"
        #       using setattr

    @abstractmethod
    def skip(self) -> None:  # pragma: no cover
        """
        Trigger the player to play the next song immediately
        """
        ...

    @abstractmethod
    def play(self) -> None:  # pragma: no cover
        """
        Start/Resume playing
        """
        ...

    @abstractmethod
    def enqueue(
        self, filename: str, is_jingle: bool = False
    ) -> None:  # pragma: no cover
        """
        Append a new song to the queue

        :param filename: The file on-disk
        :param is_jingle: Whether to consider this song as a jingle or not.
            Jingles are excluded from certain statistic calculations.
        """
        ...

    @property
    @abstractmethod
    def remaining_seconds(self) -> int:  # pragma: no cover
        """
        How many seconds until we arrive at the end of the queue
        """
        ...

    @property
    @abstractmethod
    def is_playing(self) -> bool:  # pragma: no cover
        """
        Whether the player is currently playing or not
        """
        ...

    @property
    @abstractmethod
    def is_empty(self) -> bool:  # pragma: no cover
        """
        Whether the internal playlist is empty or not
        """
        ...


class NullPlayer(AbstractPlayer):
    """
    A player which only logs the underlying calls but does nothing.
    """

    CONFIG_KEYS: Set[str] = set()

    def configure(self, cfg: Dict[str, Any]) -> None:
        pass

    def skip(self) -> None:
        self._log.debug("Skipping (no-op)")
        return

    def play(self) -> None:
        self._log.debug("Starting playback (no-op)")
        return

    def enqueue(self, filename: str, is_jingle: bool = False) -> None:
        self._log.debug("Queuing %r, jingle: %r (no-op)", filename, is_jingle)
        return None

    @property
    def remaining_seconds(self) -> int:
        self._log.debug("Returning remaining seconds")
        return 0

    @property
    def is_playing(self) -> bool:
        self._log.debug("Returning current play-state")
        return False

    @property
    def is_empty(self) -> bool:
        self._log.debug("Returning current empty-state")
        return False


class MpdPlayer(AbstractPlayer):
    """
    A bridge to a MPD daemon
    """

    CONFIG_KEYS = {"host", "port", "path_map"}

    def __init__(self, config: Optional[Config]) -> None:
        super().__init__(config)
        self.client = None
        self.path_map = PathMap(Path(""), Path(""))
        self.host = ""
        self.port = ""

    def configure(self, cfg: Dict[str, Any]) -> None:
        self.host = cfg["host"].strip()
        self.port = int(cfg["port"])
        outer_path, _, inner_path = cfg["path_map"].partition(":")
        self.path_map = PathMap(Path(outer_path), Path(inner_path))

    def jukebox2mpd(self, filename: str) -> str:
        """
        Convert a filename from the jukebox to mpd

        The filenames may differ in case the jukebox and mpd run on different
        systems (or containers). This maps a "jukebox-filename" to a
        "mpd-filename". MPD filenames are relative to the internal mpd-database
        root.
        """
        jukebox_root = str(self.path_map.jukebox_path)
        mpd_path = filename[len(jukebox_root) + 1 :]
        return str(mpd_path)

    def mpd2jukebox(self, filename: str) -> str:
        """
        Convert a filename from mpd to the jukebox.

        The filenames may differ in case the jukebox and mpd run on different
        systems (or containers). This maps a "mpd-filename" to a
        "jukebox-filename"
        """
        jb_path = self.path_map.jukebox_path / filename
        return str(jb_path)

    def connect(self) -> None:
        """
        Connect to MPD (if not yet connected)
        """
        # pylint: disable=no-member
        if self.client is not None:
            return
        self._log.info("Connecting to MPD via %s:%s", self.host, self.port)
        client = MPDClient()
        client.timeout = 10
        client.connect(self.host, self.port)  # type: ignore
        client.consume(1)  # type: ignore
        self.client = client

    def play(self) -> None:
        # pylint: disable=no-member
        self.connect()
        self.client.play()  # type: ignore

    def skip(self) -> None:
        # pylint: disable=no-member
        self.connect()
        self.client.next()  # type: ignore

    def enqueue(self, filename: str, is_jingle: bool = False) -> None:
        # pylint: disable=no-member
        if not filename.strip():
            self._log.error("Trying to enqueue an empty filename. Ignoring.")
            return
        self.connect()
        mpd_filename = self.jukebox2mpd(filename)
        self._log.info("Queuing %r (jingle=%r) to mpd", mpd_filename, is_jingle)
        try:
            self.client.add(mpd_filename)  # type: ignore
        except CommandError as exc:
            if exc.errno == FailureResponseCode.NO_EXIST:
                raise ConfigError(
                    f"MPD backend did not find {mpd_filename!r}. Sneaky cause: "
                    "Different path inside docker-container than on host. "
                    "Use 'path_map' config-option in wicked-jukebox config!"
                ) from exc
            raise
        if is_jingle:
            self.songs_since_last_jingle = 0
        else:
            self.songs_since_last_jingle += 1
        self._log.debug(
            "Songs since last jingle: %d", self.songs_since_last_jingle
        )

    @property
    def remaining_seconds(self) -> int:
        # pylint: disable=no-member
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
        self._log.debug("Remaining playtime: %3.2fs", remaining_playtime)
        return floor(remaining_playtime)

    @property
    def is_playing(self) -> bool:
        # pylint: disable=no-member
        self.connect()
        status: Dict[str, str] = self.client.status()  # type: ignore
        return status.get("state") == "play"

    @property
    def is_empty(self) -> bool:
        # pylint: disable=no-member
        self.connect()
        playlist: List[MpdSong] = self.client.playlistinfo()  # type: ignore
        return playlist == []
