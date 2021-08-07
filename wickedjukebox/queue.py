import logging
from abc import ABC, abstractmethod

from wickedjukebox.logutil import qualname


class AbstractQueue(ABC):
    def __init__(self) -> None:
        self._log = logging.getLogger(qualname(self))

    def __repr__(self) -> str:
        return f"<{qualname(self)}>"

    @abstractmethod
    def dequeue(self) -> str:
        ...


class NullQueue(AbstractQueue):
    def dequeue(self) -> str:
        self._log.debug("Dequeuing nothing")
        return ""
