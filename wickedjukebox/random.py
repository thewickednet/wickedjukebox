from abc import ABC, abstractmethod
import logging
from wickedjukebox.logutil import qualname

from wickedjukebox.adt import Song


class AbstractRandom(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._log = logging.getLogger(qualname(self))

    def __repr__(self) -> str:
        return f"<{qualname(self)}>"

    @abstractmethod
    def pick(self) -> Song:
        ...


class NullRandom(AbstractRandom):
    def pick(self) -> Song:
        return Song("", "", "", "")