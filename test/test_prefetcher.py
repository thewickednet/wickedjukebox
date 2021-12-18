# type: ignore
# pylint: skip-file
"""
This module contains unit-tests for the DB dialog between the application and
songs.
"""

from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm.session import Session

from wickedjukebox.demon.dbmodel import Song, User


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
    song = Song.smart_random(dbsession, default_data["default_channel"].name)
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
    song = Song.smart_random(dbsession, default_data["default_channel"].name)
    assert song is not None
    assert song.title == default_data["default_song"].title
