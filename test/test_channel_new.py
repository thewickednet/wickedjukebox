"""
This module contains high-level tests for a new "channel" architecture (as of
2021)
"""
from unittest.mock import call, create_autospec

from wickedjukebox.channel import Channel
from wickedjukebox.component.ipc import AbstractIPC, Command
from wickedjukebox.component.jingle import AbstractJingle
from wickedjukebox.component.player import AbstractPlayer
from wickedjukebox.component.queue import AbstractQueue
from wickedjukebox.component.random import AbstractRandom


def test_channel_init():
    """
    We want to be able to initialise a channel with a no-arg constructor without
    crash
    """
    channel = Channel()
    assert channel.name == ""


def test_tick():
    """
    A channel should have a "tick" method which is called inside an endless loop
    and represents the channel's logic. A separate "tick" method makes this
    easier to test. During one "tick" we expect the channel to perform the core
    logic to groom the backend-player playlist.
    """
    mock_random = create_autospec(AbstractRandom)
    mock_random.pick.return_value = "fake-random"
    mock_queue = create_autospec(AbstractQueue)
    mock_queue.dequeue.return_value = None
    mock_jingle = create_autospec(AbstractJingle)
    mock_jingle.pick.return_value = "fake-jingle"
    mock_jingle.interval = 10
    mock_player = create_autospec(AbstractPlayer)
    mock_player.remaining_seconds = 5
    mock_player.progress = 0
    mock_player.songs_since_last_jingle = 99
    mock_player.is_empty = False
    channel = Channel(
        player=mock_player,
        random=mock_random,
        queue=mock_queue,
        jingle=mock_jingle,
    )
    start_ticks = channel.ticks
    channel.tick()
    assert channel.ticks > start_ticks
    mock_random.pick.assert_called_once()
    mock_queue.dequeue.assert_called_once()
    mock_jingle.pick.assert_called_once()
    assert mock_player.enqueue.mock_calls == [
        call("fake-jingle", is_jingle=True),
        call("fake-random", is_jingle=False),
    ]


def test_queue_needed():
    """
    If the current song of the backend-player is close to being finished, we
    need to enqueue a new song.
    """
    mock_player = create_autospec(AbstractPlayer)
    mock_player.songs_since_last_jingle = 0
    mock_player.remaining_seconds = 5
    mock_player.progress = 0
    mock_player.is_empty = False
    mock_queue = create_autospec(AbstractQueue)
    channel = Channel(tick_interval_s=5, queue=mock_queue, player=mock_player)
    channel.tick()
    mock_player.enqueue.assert_called_once()


def test_queue_needed_empty():
    """
    If the queue of the backend-player is too short, we should enqueue a new
    file.
    """
    mock_player = create_autospec(AbstractPlayer)
    mock_player.songs_since_last_jingle = 0
    mock_player.remaining_seconds = 0
    mock_player.progress = 0
    mock_player.is_empty = False
    mock_queue = create_autospec(AbstractQueue)
    sentinel = object()
    mock_queue.dequeue.return_value = sentinel
    channel = Channel(queue=mock_queue, player=mock_player)
    channel.tick()
    mock_player.enqueue.assert_called_once_with(sentinel, is_jingle=False)


def test_random_needed():
    """
    If the current queue is empty, we expect a random song to be picked
    """
    mock_player = create_autospec(AbstractPlayer)
    mock_player.songs_since_last_jingle = 0
    mock_player.remaining_seconds = 0
    mock_player.progress = 0
    mock_player.is_empty = False
    mock_queue = create_autospec(AbstractQueue)
    mock_queue.dequeue.return_value = None
    mock_random = create_autospec(AbstractRandom)
    sentinel = object()
    mock_random.pick.return_value = sentinel
    channel = Channel(queue=mock_queue, player=mock_player, random=mock_random)
    channel.tick()
    mock_player.enqueue.assert_called_once_with(sentinel, is_jingle=False)


def test_skip_requested():
    """
    If a user requested a song-skip, we should do so.
    """
    mock_player = create_autospec(AbstractPlayer)
    mock_player.songs_since_last_jingle = 0
    mock_player.remaining_seconds = 99
    mock_player.progress = 0
    mock_ipc = create_autospec(AbstractIPC)
    fake_state = {
        Command.SKIP: 1,
    }
    mock_ipc.get.side_effect = fake_state.get
    channel = Channel(player=mock_player, ipc=mock_ipc)
    channel.tick()
    mock_player.skip.assert_called_once_with()


def test_skip_ensure_queue():
    """
    When skipping we need to enqueue something if the player has not much left
    to play in its internal queue.
    """
    mock_player = create_autospec(AbstractPlayer)
    mock_player.songs_since_last_jingle = 0
    mock_player.remaining_seconds = 0
    mock_player.progress = 0
    mock_ipc = create_autospec(AbstractIPC)
    fake_state = {
        Command.SKIP: 1,
    }
    mock_ipc.get.side_effect = fake_state.get
    mock_queue = create_autospec(AbstractQueue)
    mock_queue.dequeue.return_value = object()
    channel = Channel(player=mock_player, ipc=mock_ipc, queue=mock_queue)
    channel.tick()
    mock_player.skip.assert_called_once_with()
    mock_player.enqueue.assert_called()
