from decimal import Decimal

import pytest
from pytest_sqlalchemy import connection, dbsession, engine, transaction

from wickedjukebox.demon.dbmodel import Song
from wickedjukebox.demon.playmodes import create
from wickedjukebox.demon.playmodes.interface import RandomItem


def test_standing_count(default_data, dbsession):
    instance = create("random_wr2", session=dbsession)
    result = instance._get_standing_count(
        default_data["default_song"].id,
        [default_data["default_user"].id],
        "love",
    )
    assert result == 1

    result = instance._get_standing_count(
        default_data["default_song"].id,
        [default_data["default_user"].id],
        "hate",
    )
    assert result == 0


def test_bootstrap():
    instance = create("random_wr2", session=dbsession)
    instance.bootstrap()


@pytest.mark.skip("Legacy and probably no longer needed")
def test_fetch_candidates(default_data, dbsession):
    song = Song("/path/to/song.mp3")
    song.artist = default_data["default_artist"]
    song.album = default_data["default_album"]
    song.duration = 300
    dbsession.add(song)
    dbsession.flush()
    dbsession.refresh(song)
    instance = create(
        "random_wr2",
        channel_id=default_data["default_channel"].id,
        session=dbsession,
    )
    result = instance.fetch_candidates()
    assert len(result) == 1
    result[0].stats.pop("sortkey")
    assert result[0].song == song.id
    assert result[0].stats == {
        "score": 4.0,
        "love_count": 0,
        "duration": Decimal("300.0000"),
        "last_played": None,
    }


@pytest.mark.skip("Legacy and probably no longer needed")
def test_get(default_data, dbsession):
    song = Song("/path/to/song.mp3")
    song.artist = default_data["default_artist"]
    song.album = default_data["default_album"]
    song.duration = 300
    dbsession.add(song)
    dbsession.flush()
    dbsession.refresh(song)
    instance = create(
        "random_wr2",
        channel_id=default_data["default_channel"].id,
        session=dbsession,
    )
    result = instance.get()
    assert result.id == song.id
