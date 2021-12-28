"""
This module contains implementations for jingle-handling
"""
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from random import choice
from typing import Any, Dict, Optional, Set

from wickedjukebox.config import Config
from wickedjukebox.logutil import qualname, qualname_repr


@qualname_repr
class AbstractJingle(ABC):
    """
    This abstract class provides the interface for the underlying
    implementations
    """

    CONFIG_KEYS: Set[str] = set()

    def __init__(self, config: Optional[Config], channel_name: str) -> None:
        self._log = logging.getLogger(qualname(self))
        self._config = config
        self._channel_name = channel_name
        self.interval = 0

    @abstractmethod
    def configure(self, cfg: Dict[str, Any]) -> None:
        """
        Process configuration data from a configuration mapping. The
        required keys depend on the specific component type.
        """
        # TODO: This can be implemented in the top-class (i.e. here) by defining
        #       the expected keys as a class-variable and then "pulling them in"
        #       using setattr

    @abstractmethod
    def pick(self) -> str:
        """
        Pick a jingle to be added to the player queue
        """
        ...


class NullJingle(AbstractJingle):
    """
    A no-op implementation that simply logging the fact that we *would* play a
    jingle next.
    """

    def pick(self) -> str:
        self._log.debug("Returning 'null' jingle")
        return ""

    def configure(self, cfg: Dict[str, Any]) -> None:
        self._log.debug("Would configure 'null' jingle")


class FileBasedJingles(AbstractJingle):
    """
    An implementation of random picking based on a file-tree.

    It builds possible file-names recursively from a root and picks one file at
    random.
    """

    CONFIG_KEYS = {"root", "interval"}

    def __init__(self, config: Optional[Config], channel_name: str) -> None:
        super().__init__(config, channel_name)
        self.root = Path("")

    def configure(self, cfg: Dict[str, Any]) -> None:
        self.root = Path(cfg["root"]).resolve()
        self.interval = int(cfg.get("interval", "0"))
        self._log.info(
            "Playing jingles from %r every %d songs", self.root, self.interval
        )

    def pick(self) -> str:
        candidates = list(self.root.glob("**/*.mp3"))
        if not candidates:
            self._log.info(
                "Jingles configured using %r, but no jingles found in that "
                "folder!",
                self.root,
            )
            return ""
        pick = str(choice(candidates))
        # XXX output = str(pick.absolute())
        self._log.debug(
            "Picked %r as random file from all files in %r",
            pick,
            self.root,
        )
        return pick
