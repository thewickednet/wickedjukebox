import pytest
from pytest_sqlalchemy import connection, dbsession, engine, transaction

import wickedjukebox.core.channel as chnl
import wickedjukebox.demon.dbmodel as db


@pytest.fixture
def default_data(dbsession):
    '''
    Create the minimal necessary data to get the system up and running.
    '''
    default_group = db.Group('test-group')
    default_user = db.User('test-user', default_group)
    dbsession.add(default_user)


def test_something(dbsession, default_data):
    channel_entity = db.Channel('foobar', 'skeleton')
    channel_entity = dbsession.merge(channel_entity)
    channel = chnl.Channel(dbsession, 'foobar')
    channel.queueSong(db.Song(
        localpath='some.mp3',
        artist=db.Artist(name='Tool'),
        album=db.Album(name='Lateralus'),
    ))
