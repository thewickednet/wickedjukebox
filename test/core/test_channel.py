import pytest
from pytest_sqlalchemy import connection, dbsession, engine, transaction

import wickedjukebox.core.channel as chnl
import wickedjukebox.demon.dbmodel as db


@pytest.fixture
def pusher():
    from unittest.mock import create_autospec

    from pusher import Pusher

    yield create_autospec(Pusher)


@pytest.fixture
def channel(dbsession, default_data, pusher):
    channel_entity = db.Channel("foobar", "fake")
    channel_entity = dbsession.merge(channel_entity)
    channel = chnl.Channel(dbsession, 'foobar', pusher)
    yield channel


def test_queue_song(channel, default_data):
    channel.queueSong(default_data['default_song'])


def test_emit_queue(channel, pusher):
    channel.emit_internal_playlist()
    pusher.trigger.assert_called_with('wicked', 'internal_queue', [])
