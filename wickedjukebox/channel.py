import logging
from time import sleep
from typing import Optional

from wickedjukebox.ipc import AbstractIPC, Command, NullIPC
from wickedjukebox.jingle import AbstractJingle, NullJingle
from wickedjukebox.logutil import qualname
from wickedjukebox.player import AbstractPlayer, NullPlayer
from wickedjukebox.queue import AbstractQueue, NullQueue
from wickedjukebox.random import AbstractRandom, NullRandom


class Channel:
    def __init__(
        self,
        name: str = "",
        tick_interval_s: int = 5,
        jingle_interval: int = 5,
        autoplay: bool = True,
        queue: AbstractQueue = NullQueue(),
        random: Optional[AbstractRandom] = None,
        player: AbstractPlayer = NullPlayer(),
        ipc: AbstractIPC = NullIPC(""),
        jingle: AbstractJingle = NullJingle(),
    ):
        self.name = name
        self.player = player
        self.ipc = ipc
        self.queue = queue
        self.random = random or NullRandom(name)
        self.jingle = jingle
        self.tick_interval_s = tick_interval_s
        self.jingle_interval = jingle_interval
        self.autoplay = autoplay
        self.ticks = 0
        self.keep_running = True
        self._log = logging.getLogger(qualname(self))

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

        if self.player.songs_since_last_jingle > self.jingle_interval:
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
            self._enqueue()

        if do_skip:
            self._log.info("Skipping (via external request)")
            self._enqueue()
            self.player.skip()
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
        self._log.info("Jingle interval: %s songs", self.jingle_interval)
        while self.keep_running:
            try:
                self.tick()
                sleep(self.tick_interval_s)
            except KeyboardInterrupt:
                self._log.info("Caught SIGINT. Bye!")
                self.keep_running = False
        self._log.info("Stopping channel %r", self.name)
