# type: ignore
# pylint: skip-file
"""
This module contains unit-tests for the DB dialog between the application and
songs.
"""

from configparser import ConfigParser
from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm.session import Session

from wickedjukebox.config import Config, ConfigKeys
from wickedjukebox.core import smartfind
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


def _add_song(
    dbsession: Session,
    default_data: Dict[str, Any],
    localpath: str,
    mood_score,
):
    """Insert a second eligible song with the given mood score."""
    song = Song(localpath=localpath)
    song.artist = default_data["default_artist"]
    song.album = default_data["default_album"]
    song.title = localpath
    song.duration = 300
    song.mood_score = mood_score
    dbsession.add(song)
    dbsession.flush()
    return song


def _window(dbsession: Session, default_data: Dict[str, Any], low, high):
    default_data["default_channel"].mood_low = low
    default_data["default_channel"].mood_high = high
    dbsession.flush()


def test_find_song_mood_filters_out_of_range(
    dbsession: Session, default_data: Dict[str, Any]
):
    """With an active window, only in-range songs are candidates."""
    default_data["default_song"].mood_score = 95
    in_range = _add_song(dbsession, default_data, "in-range.mp3", 50)
    _window(dbsession, default_data, 20, 80)
    song = find_song(
        dbsession, SCORING_CONFIG, True, channel_name="test-channel"
    )
    assert song is not None
    assert song.id == in_range.id


def test_find_song_mood_null_passes(
    dbsession: Session, default_data: Dict[str, Any]
):
    """A song without a mood score always passes an active window."""
    _window(dbsession, default_data, 20, 80)
    song = find_song(
        dbsession, SCORING_CONFIG, True, channel_name="test-channel"
    )
    assert song is not None


def test_find_song_mood_fallback_never_silent(
    dbsession: Session, default_data: Dict[str, Any]
):
    """All songs outside the window: fall back to an unfiltered pick."""
    default_data["default_song"].mood_score = 95
    _window(dbsession, default_data, 20, 80)
    song = find_song(
        dbsession, SCORING_CONFIG, True, channel_name="test-channel"
    )
    assert song is not None
    assert song.id == default_data["default_song"].id


def test_find_song_without_channel_does_not_filter(
    dbsession: Session, default_data: Dict[str, Any]
):
    """No channel_name (legacy callers): mood filtering is off."""
    default_data["default_song"].mood_score = 95
    _window(dbsession, default_data, 20, 80)
    song = find_song(dbsession, SCORING_CONFIG, True)
    assert song is not None


def test_random_mood_filters_out_of_range(
    dbsession: Session, default_data: Dict[str, Any]
):
    default_data["default_song"].mood_score = 95
    in_range = _add_song(dbsession, default_data, "in-range2.mp3", 50)
    dbsession.flush()
    song = Song.random(dbsession, mood_range=(20, 80))
    assert song is not None
    assert song.id == in_range.id


def test_random_mood_null_passes(
    dbsession: Session, default_data: Dict[str, Any]
):
    song = Song.random(dbsession, mood_range=(20, 80))
    assert song is not None
    assert song.id == default_data["default_song"].id


def test_random_mood_fallback_never_silent(
    dbsession: Session, default_data: Dict[str, Any]
):
    default_data["default_song"].mood_score = 95
    dbsession.flush()
    song = Song.random(dbsession, mood_range=(20, 80))
    assert song is not None
    assert song.id == default_data["default_song"].id


def test_random_no_mood_range_unfiltered(
    dbsession: Session, default_data: Dict[str, Any]
):
    default_data["default_song"].mood_score = 95
    dbsession.flush()
    song = Song.random(dbsession)
    assert song is not None


def _pool_cfg(size):
    return {**SCORING_CONFIG, ScoringConfig.CANDIDATE_POOL_SIZE: size}


def test_find_song_pool_returns_song(
    dbsession: Session, default_data: Dict[str, Any]
):
    """With pooling on and no mood window, a pick is still returned."""
    song = find_song(dbsession, _pool_cfg(500), True)
    assert song is not None
    assert song.id == default_data["default_song"].id


def test_find_song_pool_disabled_is_unchanged(
    dbsession: Session, default_data: Dict[str, Any]
):
    """pool size 0 -> original behavior (returns the eligible song)."""
    song = find_song(dbsession, _pool_cfg(0), True)
    assert song is not None
    assert song.id == default_data["default_song"].id


def test_find_song_pool_never_silent_on_pool_miss(
    dbsession: Session, default_data: Dict[str, Any], monkeypatch
):
    """If the random pool matches nothing, fall through to the full pick."""
    monkeypatch.setattr(smartfind, "_random_id_pool", lambda *a, **k: [10**9])
    song = find_song(dbsession, _pool_cfg(500), True)
    assert song is not None
    assert song.id == default_data["default_song"].id


def test_pool_used_when_mood_off(
    dbsession: Session, default_data: Dict[str, Any], monkeypatch
):
    """No mood window -> the pool path runs."""
    calls = []
    real = smartfind._random_id_pool
    monkeypatch.setattr(
        smartfind,
        "_random_id_pool",
        lambda s, n: calls.append(n) or real(s, n),
    )
    find_song(dbsession, _pool_cfg(500), True)  # no channel_name -> mood off
    assert calls, "pool should be drawn when no mood window is active"


def test_pool_skipped_when_mood_active(
    dbsession: Session, default_data: Dict[str, Any], monkeypatch
):
    """An active mood window bounds the scan already -> pool path is skipped."""
    default_data["default_channel"].mood_low = 10
    default_data["default_channel"].mood_high = 90
    dbsession.flush()
    calls = []
    monkeypatch.setattr(
        smartfind, "_random_id_pool", lambda *a, **k: calls.append(1) or []
    )
    song = find_song(
        dbsession, _pool_cfg(500), True, channel_name="test-channel"
    )
    assert song is not None
    assert calls == [], "pool must not be drawn when a mood window is active"


def test_candidate_pool_size_optional_read():
    """Approach (b): the key is read with a fallback, so a section without it
    still yields 0 (no ConfigError), and a set value parses as int."""
    cp = ConfigParser()
    cp.add_section("channel:test:autoplay")
    cp.set("channel:test:autoplay", "type", "smart_prefetch")
    cfg = Config(cp)
    assert (
        cfg.get(
            ConfigKeys.CANDIDATE_POOL_SIZE,
            fallback=0,
            channel="test",
            converter=int,
        )
        == 0
    )
    cp.set("channel:test:autoplay", "candidate_pool_size", "500")
    assert (
        cfg.get(
            ConfigKeys.CANDIDATE_POOL_SIZE,
            fallback=0,
            channel="test",
            converter=int,
        )
        == 500
    )
