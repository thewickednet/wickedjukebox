"""
This module contains implementations for user-based queuing systems.
"""
import logging
from abc import ABC, abstractmethod

from wickedjukebox.logutil import qualname, qualname_repr


@qualname_repr
class AbstractQueue(ABC):
    """
    This class provides the interface for queuing implementations
    """

    def __init__(self) -> None:
        self._log = logging.getLogger(qualname(self))

    @abstractmethod
    def dequeue(self) -> str:
        """
        Return the filename of the song that should be played next.
        """


class NullQueue(AbstractQueue):
    """
    A queue which only logs operations, but always returns an empty filename.
    """

    def dequeue(self) -> str:
        self._log.debug("Dequeuing nothing")
        return ""
