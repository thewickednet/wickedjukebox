from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional


class States(Enum):
    SKIP_REQUESTED = "skip"


class AbstractState(ABC):
    @abstractmethod
    def get(self, key: States) -> Optional[Any]:
        ...

    @abstractmethod
    def set(self, key: States, value: Any) -> Optional[Any]:
        ...


class NullState(AbstractState):
    def get(self, key: States) -> Optional[Any]:
        return None

    def set(self, key: States, value: Any) -> Optional[Any]:
        return None
