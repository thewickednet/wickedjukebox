"""
This module contains implementations for "random" queues.
"""
import logging
import time
from abc import ABC, abstractmethod
from os.path import abspath
from pathlib import Path
from queue import Queue
from random import choice
from threading import Thread
from typing import Any, Dict, Optional, Set

from wickedjukebox.config import Config
from wickedjukebox.logutil import qualname, qualname_repr
from wickedjukebox.model.database import Session, Song


@qualname_repr
class AbstractRandom(ABC):
    """
    This class provides the interface for random implementations
    """

    #: The names of the config-keys that this instance requires to be
    #: successfully configured.
    CONFIG_KEYS: Set[str] = set()

    def __init__(self, config: Optional[Config], channel_name: str) -> None:
        super().__init__()
        self._log = logging.getLogger(qualname(self))
        self._config = config or Config()
        self.channel_name = channel_name

    @abstractmethod
    def pick(self) -> str:  # pragma: no cover
        """
        Return the filename of a song to play next.
        """

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

    CONFIG_KEYS = {"root"}

    def __init__(self, config: Optional[Config], channel_name: str) -> None:
        super().__init__(config, channel_name)
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
            return ""
        pick = choice(candidates)
        output = str(pick.absolute())
        self._log.debug(
            "Picked %r as random file from all files in %r",
            output,
            pth.absolute(),
        )
        return output


class SmartPrefetchThread(Thread):
    """
    A daemon thread which runs the expensive "smart random" query in the
    background, ensuring that a result is prefetched and readily available when
    needed.

    :param channel_name: The name of the channel that is used to fetch
        statistics from
    :param queue: A concurrency queue. This thread provides the prefetched
        filename onto this queue. If the queue is full, the thread waits until
        it becomes available again.
    """

    daemon = True

    def __init__(
        self, config: Config, channel_name: str, queue: Queue[str]
    ) -> None:
        super().__init__()
        self.channel_name = channel_name
        self.queue = queue
        self._log = logging.getLogger(qualname(self))
        self._config = config

    def run(self) -> None:
        self._log.info("Smart random prefetcher started")
        with Session() as session:  # type: ignore
            # We use a "naive" random first so we have something quickly. The
            # "smart" query is much slower.
            song = Song.random(session)  # type: ignore
            if song is None:
                self._log.error(
                    "Unable to prefetch a song using pure random. Is the DB "
                    "empty?"
                )
                return
            self._log.debug("Quick prefetch found song %r", song)
            self.queue.put(abspath(song.localpath), block=True, timeout=None)

        # Now that we have something on the (threading) queue the player should
        # have picked this up and play that song. While that song is playing, we
        # can run the slow query to fetch the next song and put it on the queue.
        # The queue is blocking which will take care of proper
        # waiting/prefetching only if needed.
        while True:
            self._log.debug("Prefetching next song via smart random...")
            song = Song.smart_random(self._config, session, self.channel_name)  # type: ignore
            if song is None:
                self._log.error(
                    "Smart random did not find any songs. Is the DB empty?"
                )
                time.sleep(5)
            else:
                self._log.debug("Smart prefetch found song %r", song)
                self.queue.put(
                    abspath(song.localpath), block=True, timeout=None
                )


class SmartPrefetch(AbstractRandom):
    """
    An implementation which queries the database for a song that make "the most
    sense" to play next according to currently connected listeners and
    persistent state of songs.

    As the query can take a long time to execute, one result will always be
    prefetched ahead of time. So the *exact* calculation is always off by one
    "play".
    """

    def __init__(self, config: Optional[Config], channel_name: str) -> None:
        super().__init__(config, channel_name)
        self.queue: Queue[str] = Queue(maxsize=1)
        self._prefetcher = SmartPrefetchThread(
            self._config, channel_name, self.queue
        )

    def configure(self, cfg: Dict[str, Any]) -> None:
        self._prefetcher.start()

    def pick(self) -> str:
        item = self.queue.get(block=True, timeout=None)
        self.queue.task_done()
        return item
