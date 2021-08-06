from abc import ABC, abstractmethod
from typing import Optional

from wickedjukebox.adt import Song


class AbstractJingle(ABC):

    @abstractmethod
    def pick(self) -> Optional[Song]:
        ...


class NullJingle(AbstractJingle):

    def pick(self) -> Optional[Song]:
        return None