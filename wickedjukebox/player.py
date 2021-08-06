import logging
from abc import ABC, abstractmethod
from typing import List

from wickedjukebox.adt import Song
from wickedjukebox.logutil import qualname


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
