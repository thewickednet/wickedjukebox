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
from typing import Any, Dict, Mapping, Optional, Set

from wickedjukebox.config import Config, ConfigKeys
from wickedjukebox.core.smartfind import ScoringConfig, find_song
from wickedjukebox.logutil import qualname, qualname_repr
from wickedjukebox.model.db.library import Song
from wickedjukebox.model.db.sameta import Session


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

    This always returns a song with an empty filename. This may very well lead
    to errors downstream. This implementation is primarily intended for use in a
    test-harness.

    .. code-block:: ini
        :caption: Configuration Example

        [channel:example:autoplay]
        type = null
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

    .. code-block:: ini
        :caption: Configuration Example

        [channel:example:autoplay]
        type = allfiles_random
        root = /path/to/music/files
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
        output = str(pick.resolve())
        self._log.debug(
            "Picked %r as random file from all files in %r",
            output,
            pth.resolve(),
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
        self,
        config: Config,
        channel_name: str,
        queue: Queue[str],
        scoring_config: Mapping[ScoringConfig, int],
    ) -> None:
        super().__init__()
        self.channel_name = channel_name
        self.queue = queue
        self.scoring_config = scoring_config
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

        is_mysql = (
            self._config.get(ConfigKeys.DSN, "").lower().startswith("mysql")
        )

        # Now that we have something on the (threading) queue the player should
        # have picked this up and play that song. While that song is playing, we
        # can run the slow query to fetch the next song and put it on the queue.
        # The queue is blocking which will take care of proper
        # waiting/prefetching only if needed.
        while True:
            self._log.debug("Prefetching next song via smart random...")
            with Session() as session:  # type: ignore
                song = find_song(
                    session,  # type: ignore
                    self.scoring_config,
                    is_mysql,
                )
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

    .. code-block:: ini
        :caption: Configuration Example

        [channel:example:autoplay]
        type = smart_prefetch

        ; No songs longer than this amount of seconds is returned
        max_duration = 600

        ; Consider users that have been offline since this amount of seconds to
        ; be "inactive"
        proofoflife_timeout = 120

        ; The "weight_*" variables define how important a given score is. The
        ; higher the value the more important it is. There is no upper bound. It
        ; uses a simple weighing calculation based on the sum of all weights.

        ; Negatively impacts song that have been played very recently
        weight_last_played = 10

        ; Positively impacts songs that have never been played
        weight_never_played = 4

        ; Positively affects songs that have been long in the DB
        weight_song_age = 1

        ; Positively affects songs that have been "liked" by users (only for
        ; those users that are actively listening)
        weight_user_rating = 4

        ; Adds additional randomness
        weight_randomness = 1
    """

    CONFIG_KEYS = {
        "max_duration",
        "proofoflife_timeout",
        "weight_last_played",
        "weight_never_played",
        "weight_randomness",
        "weight_song_age",
        "weight_user_rating",
    }

    def __init__(self, config: Optional[Config], channel_name: str) -> None:
        super().__init__(config, channel_name)
        self.queue: Queue[str] = Queue(maxsize=1)
        self.scoring_config: Dict[ScoringConfig, int] = {}

    def configure(self, cfg: Dict[str, Any]) -> None:
        self.scoring_config = {
            ScoringConfig.MAX_DURATION: int(cfg["max_duration"]),
            ScoringConfig.PROOF_OF_LIFE_TIMEOUT: int(
                cfg["proofoflife_timeout"]
            ),
            ScoringConfig.LAST_PLAYED: int(cfg["weight_last_played"]),
            ScoringConfig.NEVER_PLAYED: int(cfg["weight_never_played"]),
            ScoringConfig.RANDOMNESS: int(cfg["weight_randomness"]),
            ScoringConfig.SONG_AGE: int(cfg["weight_song_age"]),
            ScoringConfig.USER_RATING: int(cfg["weight_user_rating"]),
        }
        self._prefetcher = SmartPrefetchThread(
            self._config, self.channel_name, self.queue, self.scoring_config
        )
        self._prefetcher.start()

    def pick(self) -> str:
        item = self.queue.get(block=True, timeout=None)
        self.queue.task_done()
        return item
