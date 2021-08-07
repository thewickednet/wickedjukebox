import logging
from time import sleep

from wickedjukebox.jingle import AbstractJingle, NullJingle
from wickedjukebox.logutil import qualname
from wickedjukebox.player import AbstractPlayer, NullPlayer
from wickedjukebox.queue import AbstractQueue, NullQueue
from wickedjukebox.random import AbstractRandom, NullRandom
from wickedjukebox.xcom import AbstractState, NullState, States


class Channel:
    def __init__(
        self,
        name: str = "",
        tick_interval_s: int = 5,
        queue: AbstractQueue = NullQueue(),
        random: AbstractRandom = NullRandom(),
        player: AbstractPlayer = NullPlayer(),
        state: AbstractState = NullState(),
        jingle: AbstractJingle = NullJingle(),
    ):
        self.name = name
        self.player = player
        self.state = state
        self.queue = queue
        self.random = random
        self.jingle = jingle
        self.tick_interval_s = tick_interval_s
        self.ticks = 0
        self.jingle_interval = 5
        self.keep_running = True
        self._log = logging.getLogger(qualname(self))

    def tick(self) -> None:
        self._log.debug("tick")

        if self.player.is_empty:
            next_song = self.queue.dequeue() or self.random.pick()
            if next_song:
                self.player.enqueue(next_song, is_jingle=False)

        if not self.player.is_playing:
            self._log.info(
                "Player is currently not playing (paused or stopped). "
                "Not doing anything."
            )
            return
        do_skip = self.state.get(States.SKIP_REQUESTED)

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
            next_song = self.queue.dequeue() or self.random.pick()
            self.player.enqueue(next_song, is_jingle=False)

        if do_skip:
            self._log.info("Skipping (via external request)")
            self.player.skip()
            self.state.set(States.SKIP_REQUESTED, False)

        self.ticks += 1

    def run(self) -> None:
        self._log.info("Starting channel %r", self.name)
        self._log.info("Player type: %r", self.player)
        self._log.info("State type: %r", self.state)
        self._log.info("Queue type: %r", self.queue)
        self._log.info("Random type: %r", self.random)
        self._log.info("Jingle type: %r", self.jingle)
        self._log.info("Tick interval: %ss", self.tick_interval_s)
        self._log.info("Jingle interval: %s songs", self.jingle_interval)
        while self.keep_running:
            self.tick()
            sleep(self.tick_interval_s)
        self._log.info("Stopping channel %r", self.name)
