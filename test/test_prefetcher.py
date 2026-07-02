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
