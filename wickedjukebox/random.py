import logging
from abc import ABC, abstractmethod
from pathlib import Path
from random import choice
from typing import Any, Dict

from wickedjukebox.logutil import qualname


class AbstractRandom(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._log = logging.getLogger(qualname(self))

    def __repr__(self) -> str:
        return f"<{qualname(self)}>"

    @abstractmethod
    def pick(self) -> str:  # pragma: no cover
        ...

    @abstractmethod
    def configure(self, cfg: Dict[str, Any]) -> None:
        """
        Process configuration data from a configuration mapping. The
        required keys depend on the specific random type.
        """
        # TODO: This can be implemented in the top-class (i.e. here) by defining
        #       the expected keys as a class-variable and then "pulling them in"
        #       using setattr


class NullRandom(AbstractRandom):
    """
    Dummy implementation resulting in no-ops.

    This always returns a song with an ampty filename. This may very well lead
    to errors downstream. This implementation is primarily intended for use in a
    test-harness.
    """

    def pick(self) -> str:
        self._log.debug("Random mode is disabled. Not queueing anything")
        return ""

    def configure(self, cfg: Dict[str, Any]) -> None:
        pass


class AllFilesRandom(AbstractRandom):
    """
    An implementation of random picking based on a file-tree.

    It builds possible file-names recursively from a root and picks one file at
    random.
    """

    def __init__(self) -> None:
        super().__init__()
        self.root = ""

    def configure(self, cfg: Dict[str, Any]) -> None:
        self.root = cfg["root"].strip()

    def pick(self) -> str:
        if self.root == "":
            self._log.error(
                "%r has no 'root folder' configured. Cannot find files!", self
            )
            return ""
        pth = Path(self.root)
        candidates = list(pth.glob("**/*.mp3"))
        if not candidates:
            self._log.info(
                "Files configured using random in %r but no files "
                "found in that folder!",
                self.root,
            )
            return None
        pick = choice(candidates)
        output = str(pick.absolute())
        self._log.debug(
            "Picked %r as random file from all files in %r",
            output,
            pth.absolute(),
        )
        return output
