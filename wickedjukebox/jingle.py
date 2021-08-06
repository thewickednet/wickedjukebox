from abc import ABC, abstractmethod
import logging
from typing import Optional
from wickedjukebox.logutil import qualname

from wickedjukebox.adt import Song


class AbstractJingle(ABC):

    def __init__(self) -> None:
        self._log = logging.getLogger(qualname(self))

    def __repr__(self) -> str:
        return f"<{qualname(self)}>"

    @abstractmethod
    def pick(self) -> Optional[Song]:
        ...


class NullJingle(AbstractJingle):

    def pick(self) -> Optional[Song]:
        self._log.debug("Returning 'null' jingle")
        return None