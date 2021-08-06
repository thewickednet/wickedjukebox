from abc import ABC, abstractmethod
import logging
from typing import Optional
from wickedjukebox.logutil import qualname

from wickedjukebox.adt import Song


class AbstractQueue(ABC):
    def __init__(self) -> None:
        self._log = logging.getLogger(qualname(self))

    def __repr__(self) -> str:
        return f"<{qualname(self)}>"

    @abstractmethod
    def dequeue(self) -> Optional[Song]:
        ...


class NullQueue(AbstractQueue):
    def dequeue(self) -> Optional[Song]:
        self._log.debug("Dequeuing nothing")
        return None
