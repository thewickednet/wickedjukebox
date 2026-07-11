# type: ignore
# pylint: skip-file
"""
This module contains unit-tests for the DB dialog between the application and
songs.
"""

from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm.session import Session

from wickedjukebox.config import Config
from wickedjukebox.core.smartfind import ScoringConfig, find_song
from wickedjukebox.model.db.auth import User
from wickedjukebox.model.db.library import Song
from wickedjukebox.model.db.playback import Channel

SCORING_CONFIG = {
    ScoringConfig.USER_RATING: 4,
    ScoringConfig.LAST_PLAYED: 4,
    ScoringConfig.SONG_AGE: 4,
    ScoringConfig.NEVER_PLAYED: 4,
    ScoringConfig.RANDOMNESS: 4,
    ScoringConfig.MAX_DURATION: 600,
    ScoringConfig.PROOF_OF_LIFE_TIMEOUT: 120,
}


def test_random(dbsession: Session, default_data: Dict[str, Any]):
    """ "
    We want to be able to fetch a song at a "complete"/naive random.
    """
    song = Song.random(dbsession)
    assert song is not None
    assert song.title == default_data["default_song"].title


def test_smart_random(dbsession: Session, default_data: Dict[str, Any]):
    """
    We want to be able to execute a "smart" random which takes various
    statistics into account.
    """
    song = find_song(dbsession, SCORING_CONFIG, True)
    assert song is not None
    assert song.title == default_data["default_song"].title


def test_smart_random_with_users(
    dbsession: Session, default_data: Dict[str, Any]
):
    """
    We want to be able to execute a "smart" random which takes various
    statistics into account.
    """
    user = dbsession.query(User).first()
    # Flag a user as "listening" so the user-query triggers
    user.proof_of_listening = datetime.now()
    dbsession.flush()
    song = find_song(dbsession, SCORING_CONFIG, True)
    assert song is not None
    assert song.title == default_data["default_song"].title


def test_exclude_from_random_defaults_to_false(
    dbsession: Session, default_data: Dict[str, Any]
):
    """
    A freshly-inserted song must default to NOT excluded (server_default 0),
    and the column must be non-nullable.
    """
    song = default_data["default_song"]
    dbsession.refresh(song)
    assert song.exclude_from_random is not None
    assert not song.exclude_from_random


def test_find_song_skips_excluded(
    dbsession: Session, default_data: Dict[str, Any]
):
    """
    A song flagged exclude_from_random must never be returned by find_song.
    With the only song excluded, find_song must return None.
    """
    default_data["default_song"].exclude_from_random = True
    dbsession.flush()
    assert find_song(dbsession, SCORING_CONFIG, True) is None


def test_find_song_respects_max_duration(
    dbsession: Session, default_data: Dict[str, Any]
):
    """
    find_song must not return a song longer than MAX_DURATION. With the only
    song over the cap, find_song must return None.
    """
    default_data["default_song"].duration = 900  # > 600 (SCORING_CONFIG cap)
    dbsession.flush()
    assert find_song(dbsession, SCORING_CONFIG, True) is None


def test_random_skips_excluded(
    dbsession: Session, default_data: Dict[str, Any]
):
    """Song.random must not return an exclude_from_random song."""
    default_data["default_song"].exclude_from_random = True
    dbsession.flush()
    assert Song.random(dbsession) is None


def test_random_skips_broken(dbsession: Session, default_data: Dict[str, Any]):
    """Song.random must not return a broken song."""
    default_data["default_song"].broken = True
    dbsession.flush()
    assert Song.random(dbsession) is None


def test_random_respects_max_duration(
    dbsession: Session, default_data: Dict[str, Any]
):
    """Song.random must not return a song longer than max_duration."""
    default_data["default_song"].duration = 900
    dbsession.flush()
    assert Song.random(dbsession, max_duration=600) is None


def test_random_returns_eligible_under_max_duration(
    dbsession: Session, default_data: Dict[str, Any]
):
    """
    Song.random must still return an eligible song whose duration is under
    the cap (default_song duration is 300 < 600).
    """
    song = Song.random(dbsession, max_duration=600)
    assert song is not None
    assert song.id == default_data["default_song"].id


def test_channel_mood_range_unknown_channel(
    dbsession: Session, default_data: Dict[str, Any]
):
    """An unknown channel name means no filtering."""
    assert Channel.mood_range(dbsession, "no-such-channel") is None


def test_channel_mood_range_off(
    dbsession: Session, default_data: Dict[str, Any]
):
    """Both thresholds NULL (the default) means filtering is off."""
    assert Channel.mood_range(dbsession, "test-channel") is None


def test_channel_mood_range_half_set(
    dbsession: Session, default_data: Dict[str, Any]
):
    """A half-set window (only one threshold) is treated as off."""
    default_data["default_channel"].mood_low = 10
    dbsession.flush()
    assert Channel.mood_range(dbsession, "test-channel") is None


def test_channel_mood_range_active(
    dbsession: Session, default_data: Dict[str, Any]
):
    """Both thresholds set: the window is returned as a tuple."""
    default_data["default_channel"].mood_low = 10
    default_data["default_channel"].mood_high = 90
    dbsession.flush()
    assert Channel.mood_range(dbsession, "test-channel") == (10, 90)
