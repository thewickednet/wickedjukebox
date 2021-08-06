from abc import ABC, abstractmethod
from typing import Optional

from wickedjukebox.adt import Song


class AbstractQueue(ABC):
    @abstractmethod
    def dequeue(self) -> Optional[Song]:
        ...


class NullQueue(AbstractQueue):
    def dequeue(self) -> Song:
        return None