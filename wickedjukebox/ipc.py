import logging
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Set

from wickedjukebox.config import Config, ConfigKeys
from wickedjukebox.demon.dbmodel import Session, State
from wickedjukebox.exc import ConfigError
from wickedjukebox.logutil import qualname

LOG = logging.getLogger(__name__)


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
    #: The names of the config-keys that this instance requires to be
    #: successfully configured.
    CONFIG_KEYS: Set[str] = set()

    def __init__(self, channel_name: str) -> None:
        self._log = logging.getLogger(qualname(self))
        self._channel_name = channel_name

    def __repr__(self) -> str:
        return f"<{qualname(self)}>"

    def configure(self, cfg: Dict[str, Any]) -> None:
        """
        Process configuration data from a configuration mapping. The
        required keys depend on the specific random type.
        """

    @abstractmethod
    def get(self, key: Command) -> Optional[Any]:  # pragma: no cover
        ...

    @abstractmethod
    def set(
        self, key: Command, value: Any
    ) -> Optional[Any]:  # pragma: no cover
        ...


class NullIPC(AbstractIPC):
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

    CONFIG_KEYS = {"path"}
    _root: Optional[Path]

    def __init__(self, channel_name: str) -> None:
        super().__init__(channel_name)
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
        self._root = Path(cfg["path"].strip()) / self._channel_name

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


class DBIPC(AbstractIPC):
    """
    Read IPC sentinel values from the database
    """

    def __init__(self, channel_name: str) -> None:
        super().__init__(channel_name)
        dsn = Config.get(ConfigKeys.DSN, "")
        if not dsn:
            raise ConfigError("No DSN available for DB-IPC")

    def get(self, key: Command) -> Optional[Any]:  # pragma: no cover
        from wickedjukebox.demon.dbmodel import Channel

        skip_state = False
        with Session() as session:  # type: ignore
            query = session.query(Channel)
            query = query.filter(Channel.name == self._channel_name)
            channel = query.one()
            if key == Command.SKIP:
                skip_state = bool(
                    int(State.get("skipping", channel.id, default=False))
                )
            else:
                LOG.error(f"Unknown IPC command: {key!r}")
        return skip_state

    def set(
        self, key: Command, value: Any
    ) -> Optional[Any]:  # pragma: no cover
        from wickedjukebox.demon.dbmodel import Channel

        skip_state = False
        with Session() as session:  # type: ignore
            query = session.query(Channel)
            query = query.filter(Channel.name == self._channel_name)
            channel = query.one()
            if key == Command.SKIP:
                skip_state = State.set("skipping", value, channel.id)
            else:
                LOG.error(f"Unknown IPC command: {key!r}")
            session.commit()
        return skip_state
