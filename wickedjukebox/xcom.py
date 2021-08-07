import logging
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from wickedjukebox.logutil import qualname


class InvalidStateRequest(Exception):
    pass


class FSStateFiles(Enum):
    """
    An enum of possible file-names in this state
    """

    SKIP_REQUESTED = "skip"


class States(Enum):
    SKIP_REQUESTED = "skip"


class AbstractState(ABC):
    def __init__(self) -> None:
        self._log = logging.getLogger(qualname(self))

    def __repr__(self) -> str:
        return f"<{qualname(self)}>"

    @abstractmethod
    def get(self, key: States) -> Optional[Any]:  # pragma: no cover
        ...

    @abstractmethod
    def set(self, key: States, value: Any) -> Optional[Any]:  # pragma: no cover
        ...


class NullState(AbstractState):
    def get(self, key: States) -> Optional[Any]:
        self._log.debug("Retrieving state for %r (no-op)", key)
        return None

    def set(self, key: States, value: Any) -> Optional[Any]:
        self._log.debug("Setting state for %r to %r (no-op)", key, value)
        return None


class FSState(AbstractState):
    """
    A no-db solution for IPC using simple files on disk
    """

    def __init__(self, root: str) -> None:
        super().__init__()
        self.root = Path(root)

    def ensure_root_exists(self) -> None:
        if not self.root.exists():
            self.root.mkdir(parents=True, exist_ok=True)

    def _exists(self, file: FSStateFiles) -> bool:
        self.ensure_root_exists()
        pth = self.root / Path(file.value)
        return pth.exists()

    def _set_boolfile(self, file: FSStateFiles, value: bool) -> None:
        self.ensure_root_exists()
        pth = self.root / Path(file.value)
        if value is True:
            pth.touch()
        elif value is False and pth.exists():
            pth.unlink()

    def get(self, key: States) -> Optional[Any]:
        if key == States.SKIP_REQUESTED:
            return self._exists(FSStateFiles.SKIP_REQUESTED)
        raise InvalidStateRequest(
            "State {key} is not (yet) supported by {self!r}"
        )

    def set(self, key: States, value: Any) -> Optional[Any]:
        if key == States.SKIP_REQUESTED:
            return self._set_boolfile(FSStateFiles.SKIP_REQUESTED, value)
        raise InvalidStateRequest(
            "State {key} is not (yet) supported by {self!r}"
        )
