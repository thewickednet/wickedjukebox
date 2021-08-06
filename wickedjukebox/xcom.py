from abc import ABC, abstractmethod
from enum import Enum
import logging
from typing import Any, Optional
from wickedjukebox.logutil import qualname


class States(Enum):
    SKIP_REQUESTED = "skip"


class AbstractState(ABC):
    def __init__(self) -> None:
        self._log = logging.getLogger(qualname(self))

    def __repr__(self) -> str:
        return f"<{qualname(self)}>"

    @abstractmethod
    def get(self, key: States) -> Optional[Any]:
        ...

    @abstractmethod
    def set(self, key: States, value: Any) -> Optional[Any]:
        ...


class NullState(AbstractState):
    def get(self, key: States) -> Optional[Any]:
        self._log.debug("Retrieving state for %r (no-op)", key)
        return None

    def set(self, key: States, value: Any) -> Optional[Any]:
        self._log.debug("Setting state for %r to %r (no-op)", key, value)
        return None
