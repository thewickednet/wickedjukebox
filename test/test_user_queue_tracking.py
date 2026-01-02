"""
Tests for tracking user-queued songs in UserSongStat model
"""

from unittest.mock import create_autospec

from wickedjukebox.channel import Channel
from wickedjukebox.component.player import AbstractPlayer
from wickedjukebox.component.queue import AbstractQueue


def test_queue_tracks_user_id():
    """
    When a song is dequeued from the user queue, the user_id should be
    tracked and associated with the filename.
    """
    mock_player = create_autospec(AbstractPlayer)
    mock_player.songs_since_last_jingle = 0
    mock_player.remaining_seconds = 99
    mock_player.progress = 0
    mock_player.is_empty = False
    mock_player.is_playing = True

    mock_queue = create_autospec(AbstractQueue)
    mock_queue.dequeue.return_value = "test-song.mp3"
    mock_queue.last_dequeued_user_id = 42

    channel = Channel(name="test-channel", queue=mock_queue, player=mock_player)

    # Simulate enqueueing a song
    channel._enqueue()

    # Verify the user_id is tracked
    assert "test-song.mp3" in channel._queued_songs
    assert channel._queued_songs["test-song.mp3"] == 42


def test_queue_tracks_user_id_only_when_present():
    """
    When a song is dequeued and no user_id is associated (e.g., from random
    playlist), the filename should not be tracked.
    """
    mock_player = create_autospec(AbstractPlayer)
    mock_player.songs_since_last_jingle = 0
    mock_player.remaining_seconds = 99
    mock_player.progress = 0
    mock_player.is_empty = False
    mock_player.is_playing = True

    mock_queue = create_autospec(AbstractQueue)
    mock_queue.dequeue.return_value = "test-song.mp3"
    mock_queue.last_dequeued_user_id = None

    channel = Channel(name="test-channel", queue=mock_queue, player=mock_player)

    # Simulate enqueueing a song
    channel._enqueue()

    # Verify the user_id is NOT tracked when None
    assert "test-song.mp3" not in channel._queued_songs


def test_queued_songs_dictionary_initialized():
    """
    The Channel should initialize with an empty _queued_songs dictionary
    """
    channel = Channel()
    assert hasattr(channel, "_queued_songs")
    assert isinstance(channel._queued_songs, dict)
    assert len(channel._queued_songs) == 0
