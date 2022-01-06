import logging
from datetime import datetime
from time import sleep
from typing import Optional

from sqlalchemy.orm import Session as TSession

from wickedjukebox.component.ipc import AbstractIPC, Command, NullIPC
from wickedjukebox.component.jingle import AbstractJingle, NullJingle
from wickedjukebox.component.player import AbstractPlayer, NullPlayer
from wickedjukebox.component.queue import AbstractQueue, NullQueue
from wickedjukebox.component.random import AbstractRandom, NullRandom
from wickedjukebox.exc import WickedJukeboxException
from wickedjukebox.logutil import qualname
from wickedjukebox.model.db.library import Song
from wickedjukebox.model.db.playback import Channel as DbChannel
from wickedjukebox.model.db.sameta import Session
from wickedjukebox.model.db.stats import ChannelStat

LOG = logging.getLogger(__name__)


class Channel:
    def __init__(
        self,
        name: str = "",
        tick_interval_s: int = 5,
        autoplay: bool = True,
        queue: AbstractQueue = NullQueue(None, ""),
        random: Optional[AbstractRandom] = None,
        player: AbstractPlayer = NullPlayer(None, ""),
        ipc: AbstractIPC = NullIPC(None, ""),
        jingle: AbstractJingle = NullJingle(None, ""),
    ):
        self.name = name
        self.player = player
        self.ipc = ipc
        self.queue = queue
        self.random = random or NullRandom(None, name)
        self.jingle = jingle
        self.tick_interval_s = tick_interval_s
        self.autoplay = autoplay
        self.ticks = 0
        self.keep_running = True
        self._log = logging.getLogger(qualname(self))

    def _log_skip_stats(self) -> None:
        filename = self.player.current_song
        if filename == "":
            LOG.debug(
                "Nothing is currently playing. Nothing committed to history"
            )
            return

        with Session() as session:  # type: ignore
            session: TSession
            song = Song.by_filename(session, filename)
            if song is None:
                LOG.warning(
                    (
                        "No song found with filename %r in database. "
                        "Not committing it to history."
                    ),
                    filename,
                )
                return
            channel = DbChannel.by_name(session, self.name)
            if channel is None:
                raise WickedJukeboxException(
                    f"No channel with name {self.name!r} found!"
                )
            stat = ChannelStat.by_song(session, song, channel)
            stat.skipped = (stat.skipped + 1) if stat.skipped else 1  # type: ignore
            session.commit()

    def _commit_song_to_history(self) -> None:
        filename = self.player.current_song
        if filename == "":
            LOG.debug(
                "Nothing is currently playing. Nothing committed to history"
            )
            return

        with Session() as session:  # type: ignore
            session: TSession
            song = Song.by_filename(session, filename)
            if song is None:
                LOG.warning(
                    (
                        "No song found with filename %r in database. "
                        "Not committing it to history."
                    ),
                    filename,
                )
                return
            channel = DbChannel.by_name(session, self.name)
            if channel is None:
                raise WickedJukeboxException(
                    f"No channel with name {self.name!r} found!"
                )
            stat = ChannelStat.by_song(session, song, channel)
            stat.lastPlayed = datetime.now()
            stat.played = (stat.played + 1) if stat.played else 1  # type: ignore
            session.commit()

    def _enqueue(self) -> None:
        next_song = self.queue.dequeue() or self.random.pick()
        if next_song:
            self.player.enqueue(next_song, is_jingle=False)

    def tick(self) -> None:
        self._log.debug("tick")

        if self.player.is_empty:
            self._enqueue()

        if not self.player.is_playing:
            if not self.autoplay:
                self._log.info(
                    "Player is currently not playing (paused or stopped). "
                    "Autoplay is disabled -> Not doing anything."
                )
                return
            else:
                self.player.play()

        do_skip = self.ipc.get(Command.SKIP)
        self.ipc.set(Command.CURRENT_SONG, self.player.current_song)
        self.ipc.set(Command.PROGRESS, self.player.progress)

        if self.player.songs_since_last_jingle > self.jingle.interval:
            self._log.debug("Jingle interval surpassed. Enqueueing new jingle.")
            jingle = self.jingle.pick()
            if jingle:
                self.player.enqueue(jingle, is_jingle=True)
            else:
                self._log.debug("no jingle available.")

        if self.player.remaining_seconds <= self.tick_interval_s:
            self._log.debug(
                "Internal player only has %d seconds left on its queue. "
                "Enqueueing new song.",
                self.player.remaining_seconds,
            )
            self._commit_song_to_history()
            self._enqueue()

        if do_skip:
            self._log.info("Skipping (via external request)")
            self._enqueue()
            self.player.skip()
            self._log_skip_stats()
            self.ipc.set(Command.SKIP, False)

        self.ticks += 1

    def run(self) -> None:
        self._log.info("Starting channel %r", self.name)
        self._log.info("Player type: %r", self.player)
        self._log.info("IPC type: %r", self.ipc)
        self._log.info("Queue type: %r", self.queue)
        self._log.info("Random type: %r", self.random)
        self._log.info("Jingle type: %r", self.jingle)
        self._log.info("Tick interval: %ss", self.tick_interval_s)
        while self.keep_running:
            try:
                self.tick()
                sleep(self.tick_interval_s)
            except KeyboardInterrupt:
                self._log.info("Caught SIGINT. Bye!")
                self.keep_running = False
        self._log.info("Stopping channel %r", self.name)
