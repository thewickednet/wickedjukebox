import logging
from abc import ABC, abstractmethod
from pathlib import Path
from random import choice
from typing import Optional

from wickedjukebox.adt import Song
from wickedjukebox.logutil import qualname


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


class FileBasedJingles(AbstractJingle):
    """
    An implementation of random picking based on a file-tree.

    It builds possible file-names recursively from a root and picks one file at
    random.
    """

    def __init__(self, root: str) -> None:
        super().__init__()
        self.root = root

    def pick(self) -> Optional[Song]:
        pth = Path(self.root)
        candidates = list(pth.glob("**/*.mp3"))
        if not candidates:
            self._log.info(
                "Jingles configured using %r, but no jingles found in that "
                "folder!",
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
        return Song("", "", "", output)
