"""
This module contains implementations for inter-process calls.

IPC modules allow external applications to trigger certain behaviour in the
jukebox like skipping the currently running song for example.
"""
import logging
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Set

from wickedjukebox.config import Config, ConfigKeys
from wickedjukebox.exc import ConfigError
from wickedjukebox.logutil import qualname, qualname_repr
from wickedjukebox.model.db.playback import Channel, State
from wickedjukebox.model.db.sameta import Session

LOG = logging.getLogger(__name__)
"The module logger"


class InvalidCommand(Exception):
    """
    Raise if we got an invalid IPC command from the outside world
    """


class FSStateFiles(Enum):
    """
    An enum of possible file-names in this state
    """

    SKIP_REQUESTED = "skip"
    """
    If this file exists, the running song will be skipped and this file will
    be removed
    """


class Command(Enum):
    """
    Possible commands that can be interpreted
    """

    SKIP = "skip"
    "Skip the current song as soon as possible"
    CURRENT_SONG = "current_song"
    PROGRESS = "progress"


@qualname_repr
class AbstractIPC(ABC):
    """
    The abstract IPC class provides an interface for the undelying
    implementations.
    """

    #: The names of the config-keys that this instance requires to be
    #: successfully configured.
    CONFIG_KEYS: Set[str] = set()

    def __init__(self, config: Optional[Config], channel_name: str) -> None:
        self._log = logging.getLogger(qualname(self))
        self._channel_name = channel_name
        self._config = config

    def configure(self, cfg: Dict[str, Any]) -> None:
        """
        Process configuration data from a configuration mapping. The
        required keys depend on the specific random type.
        """

    @abstractmethod
    def get(self, key: Command) -> Optional[Any]:  # pragma: no cover
        """
        Get the currentl state of a given command.
        """
        ...

    @abstractmethod
    def set(
        self, key: Command, value: Any
    ) -> Optional[Any]:  # pragma: no cover
        """
        Set the new state of a given command
        """
        ...


class NullIPC(AbstractIPC):
    """
    An IPC implementation where each command is a simple no-op.

    Commands are logged, no other action is taken.

    .. code-block:: ini
        :caption: Configuration Example

        [channel:example:ipc]
        type = null
    """

    def get(self, key: Command) -> Optional[Any]:
        self._log.debug("Retrieving command for %r (no-op)", key)
        return None

    def set(self, key: Command, value: Any) -> Optional[Any]:
        self._log.debug("Setting command for %r to %r (no-op)", key, value)
        return None


class FSIPC(AbstractIPC):
    """
    A no-db solution for IPC using simple files on disk.

    Each command is represented as a single plain-text file in a given folder.
    If the command requires a value/argument it will use the content of the file
    as such.

    .. code-block:: ini
        :caption: Configuration Example

        [channel:example:ipc]
        type = fs
        path = /path/to/ipc-files

    Commands like "skip" can simply be executed by creating an empty file named
    "skip" into the folder:

    .. code-block:: bash

        touch /path/to/ipc-files/skip
    """

    CONFIG_KEYS = {"path"}
    _root: Optional[Path]

    def __init__(self, config: Optional[Config], channel_name: str) -> None:
        super().__init__(config, channel_name)
        self._root = None

    def __repr__(self) -> str:
        pth = str(self._root.resolve()) if self._root else ""
        return f"{super().__repr__()[:-1]} path={pth!r}>"

    @property
    def root(self) -> Path:
        """
        The root folder for this IPC instance
        """
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
        """
        Check if a given file exists in this IPCs base folder
        """
        pth = self.root / Path(file.value)
        return pth.exists()

    def _set_boolfile(self, file: FSStateFiles, value: bool) -> None:
        """
        Use an file-existence as boolean check. If *value* is true, create the
        file, if it is false, remove the file.
        """
        pth = self.root / Path(file.value)
        if value is True:
            pth.touch()
        elif value is False and pth.exists():
            pth.unlink()

    def get(self, key: Command) -> Optional[Any]:
        if key == Command.SKIP:
            return self._exists(FSStateFiles.SKIP_REQUESTED)
        raise InvalidCommand(
            f"Command {key} is not (yet) supported by {self!r}"
        )

    def set(self, key: Command, value: Any) -> Optional[Any]:
        if key == Command.SKIP:
            return self._set_boolfile(FSStateFiles.SKIP_REQUESTED, value)
        raise InvalidCommand(
            f"Command {key} is not (yet) supported by {self!r}"
        )


class DBIPC(AbstractIPC):
    """
    An IPC implementation using the underlying database as backend. This relies
    on the ``state`` table defined in the default database schema.

    .. code-block:: ini
        :caption: Configuration Example

        [channel:example:ipc]
        type = db
    """

    def __init__(self, config: Optional[Config], channel_name: str) -> None:
        super().__init__(config, channel_name)
        dsn = self._config.get(ConfigKeys.DSN, "")
        if not dsn:
            raise ConfigError("No DSN available for DB-IPC")

    def get(self, key: Command) -> Optional[Any]:  # pragma: no cover

        skip_state = False
        with Session() as session:  # type: ignore
            query = session.query(Channel)  # type: ignore
            query = query.filter(Channel.name == self._channel_name)  # type: ignore
            channel = query.one()  # type: ignore
            if key == Command.SKIP:
                result = State.get("skipping", channel.id, default=False) or "0"
                skip_state = bool(int(result))  # type: ignore
            else:
                LOG.error("Unknown IPC command: %r", key)
        return skip_state

    def set(
        self, key: Command, value: Any
    ) -> Optional[Any]:  # pragma: no cover

        skip_state = False
        with Session() as session:  # type: ignore
            query = session.query(Channel)  # type: ignore
            query = query.filter(Channel.name == self._channel_name)  # type: ignore
            channel = query.one()  # type: ignore
            if key == Command.SKIP:
                output = State.set(  # type: ignore
                    "skipping", value, channel.id  # type: ignore
                )
                output = "0"
            elif key == Command.CURRENT_SONG:
                output = State.set(  # type: ignore
                    "current_song", value, channel.id  # type: ignore
                )
            elif key == Command.PROGRESS:
                output = State.set(  # type: ignore
                    "progress", value, channel.id  # type: ignore
                )
            else:
                LOG.error("Unknown IPC command: %r", key)
            session.commit()  # type: ignore
        return output
