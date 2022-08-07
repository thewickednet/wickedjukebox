"""
This module contains implementations for user-based queuing systems.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Set

from wickedjukebox.config import Config
from wickedjukebox.logutil import qualname, qualname_repr
from wickedjukebox.model.db.playback import QueueItem
from wickedjukebox.model.db.sameta import Session


@qualname_repr
class AbstractQueue(ABC):
    """
    This class provides the interface for queuing implementations
    """

    CONFIG_KEYS: Set[str] = set()

    def __init__(self, config: Optional[Config], channel_name: str) -> None:
        self._channel_name = channel_name
        self._config = config or Config()
        self._log = logging.getLogger(qualname(self))

    def configure(self, cfg: Dict[str, Any]) -> None:
        """
        Process configuration data from a configuration mapping. The
        required keys depend on the specific random type.
        """

    @abstractmethod
    def dequeue(self) -> str:
        """
        Return the filename of the song that should be played next.
        """


class NullQueue(AbstractQueue):
    """
    A queue which only logs operations, but always returns an empty filename.

    .. code-block:: ini
        :caption: Configuration Example

        [channel:example:queue]
        type = null
    """

    def dequeue(self) -> str:
        self._log.debug("Dequeuing nothing")
        return ""


class DatabaseQueue(AbstractQueue):
    """
    A queue which is backed by a database storage. This uses the ``queue`` table
    from the default DB-Schema.

    .. code-block:: ini
        :caption: Configuration Example

        [channel:example:queue]
        type = db
    """

    def dequeue(self) -> str:
        with Session() as session:  # type: ignore
            queue_item = QueueItem.next(session, self._channel_name)  # type: ignore
            if not queue_item:
                self._log.debug("No item on queue at position 0")
                return ""
            QueueItem.advance(session, self._channel_name)  # type: ignore
            session.commit()  # type: ignore
            self._log.debug("Dequeued %r", queue_item.song)  # type: ignore
            return queue_item.song.localpath  # type: ignore
