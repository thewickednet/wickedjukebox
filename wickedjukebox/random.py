import logging
from abc import ABC, abstractmethod
from pathlib import Path
from random import choice

from wickedjukebox.adt import Song
from wickedjukebox.logutil import qualname


class AbstractRandom(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._log = logging.getLogger(qualname(self))

    def __repr__(self) -> str:
        return f"<{qualname(self)}>"

    @abstractmethod
    def pick(self) -> Song:
        ...


class NullRandom(AbstractRandom):
    """
    Dummy implementation resulting in no-ops.

    This always returns a song with an ampty filename. This may very well lead
    to errors downstream. This implementation is primarily intended for use in a
    test-harness.
    """

    def pick(self) -> Song:
        return Song("", "", "", "")


class AllFilesRandom(AbstractRandom):
    """
    An implementation of random picking based on a file-tree.

    It builds possible file-names recursively from a root and picks one file at
    random.
    """

    def __init__(self, root: str) -> None:
        super().__init__()
        self.root = root

    def pick(self) -> Song:
        pth = Path(self.root)
        pick = choice(list(pth.glob("**/*.mp3")))
        output = Song("", "", "", str(pick.absolute()))
        self._log.debug(
            "Picked %r as random file from all files in %r",
            output,
            pth.absolute(),
        )
        return output
