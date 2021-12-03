import logging
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from wickedjukebox.exc import ConfigError
from wickedjukebox.logutil import qualname


class InvalidCommand(Exception):
    pass


class FSStateFiles(Enum):
    """
    An enum of possible file-names in this state
    """

    SKIP_REQUESTED = "skip"


class Command(Enum):
    SKIP = "skip"


class AbstractIPC(ABC):
    def __init__(self) -> None:
        self._log = logging.getLogger(qualname(self))

    def __repr__(self) -> str:
        return f"<{qualname(self)}>"

    @abstractmethod
    def configure(self, cfg: Dict[str, Any]) -> None:
        """
        Process configuration data from a configuration mapping. The
        required keys depend on the specific random type.
        """
        # TODO: This can be implemented in the top-class (i.e. here) by defining
        #       the expected keys as a class-variable and then "pulling them in"
        #       using setattr

    @abstractmethod
    def get(self, key: Command) -> Optional[Any]:  # pragma: no cover
        ...

    @abstractmethod
    def set(
        self, key: Command, value: Any
    ) -> Optional[Any]:  # pragma: no cover
        ...


class NullIPC(AbstractIPC):
    def configure(self, cfg: Dict[str, Any]) -> None:
        pass

    def get(self, key: Command) -> Optional[Any]:
        self._log.debug("Retrieving command for %r (no-op)", key)
        return None

    def set(self, key: Command, value: Any) -> Optional[Any]:
        self._log.debug("Setting command for %r to %r (no-op)", key, value)
        return None


class FSIPC(AbstractIPC):
    """
    A no-db solution for IPC using simple files on disk
    """

    root: Optional[Path]

    def __init__(self) -> None:
        super().__init__()
        self._root = None

    def __repr__(self) -> str:
        pth = str(self._root.absolute()) if self._root else ""
        return f"<{qualname(self)} path={pth!r}>"

    @property
    def root(self) -> Path:
        if self._root is None:
            raise ConfigError(f"Invalid path ({self.root!r} for file-based IPC")
        return self._root

    @root.setter
    def root(self, pth: Path) -> None:
        self._root = pth
        if not pth.exists():
            pth.mkdir(parents=True, exist_ok=True)

    def configure(self, cfg: Dict[str, Any]) -> None:
        self._root = Path(cfg["path"].strip())

    def _exists(self, file: FSStateFiles) -> bool:
        pth = self.root / Path(file.value)
        return pth.exists()

    def _set_boolfile(self, file: FSStateFiles, value: bool) -> None:
        pth = self.root / Path(file.value)
        if value is True:
            pth.touch()
        elif value is False and pth.exists():
            pth.unlink()

    def get(self, key: Command) -> Optional[Any]:
        if key == Command.SKIP:
            return self._exists(FSStateFiles.SKIP_REQUESTED)
        raise InvalidCommand("Command {key} is not (yet) supported by {self!r}")

    def set(self, key: Command, value: Any) -> Optional[Any]:
        if key == Command.SKIP:
            return self._set_boolfile(FSStateFiles.SKIP_REQUESTED, value)
        raise InvalidCommand("Command {key} is not (yet) supported by {self!r}")
