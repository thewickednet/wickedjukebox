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
