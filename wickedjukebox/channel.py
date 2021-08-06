import logging
from time import sleep

from wickedjukebox.jingle import AbstractJingle, NullJingle
from wickedjukebox.player import AbstractPlayer, NullPlayer
from wickedjukebox.queue import AbstractQueue, NullQueue
from wickedjukebox.random import AbstractRandom, NullRandom
from wickedjukebox.xcom import AbstractState, NullState, States

LOG = logging.getLogger(__name__)


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

    def tick(self) -> None:
        do_skip = self.state.get(States.SKIP_REQUESTED)

        if self.player.songs_since_last_jingle > self.jingle_interval:
            LOG.debug("Jingle interval surpassed. Enqueueing new jingle.")
            jingle = self.jingle.pick()
            if jingle:
                self.player.enqueue(jingle)
            else:
                LOG.debug("no jingle available.")

        if self.player.remaining_seconds <= self.tick_interval_s:
            LOG.debug(
                "Internal player only has %d seconds left on its queue. "
                "Enqueueing new song.",
                self.player.remaining_seconds,
            )
            next_song = self.queue.dequeue() or self.random.pick()
            self.player.enqueue(next_song)

        if do_skip:
            LOG.info("Skipping (via external request)")
            self.player.skip()
            self.state.set(States.SKIP_REQUESTED, False)

        self.ticks += 1

    def run(self) -> None:
        while self.keep_running:
            self.tick()
            sleep(self.tick_interval_s)
