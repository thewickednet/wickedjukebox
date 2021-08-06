from abc import ABC, abstractmethod
from typing import List

from wickedjukebox.adt import Song


class AbstractPlayer(ABC):

    def __init__(self) -> None:
        self.songs_since_last_jingle = 0

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
        return

    def enqueue(self, song: Song, is_jingle: bool = False) -> None:
        return None

    @property
    def remaining_seconds(self) -> int:
        return 0

    @property
    def upcoming_songs(self) -> List[Song]:
        return []
