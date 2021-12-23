import logging
from abc import ABC, abstractmethod

from wickedjukebox.logutil import qualname, qualname_repr


@qualname_repr
class AbstractQueue(ABC):
    def __init__(self) -> None:
        self._log = logging.getLogger(qualname(self))

    @abstractmethod
    def dequeue(self) -> str:
        ...


class NullQueue(AbstractQueue):
    def dequeue(self) -> str:
        self._log.debug("Dequeuing nothing")
        return ""
