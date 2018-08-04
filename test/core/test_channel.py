import pytest
import wickedjukebox.core.channel as chnl
import wickedjukebox.demon.dbmodel as db
from pytest_sqlalchemy import connection, dbsession, engine, transaction


@pytest.fixture
def default_data(dbsession):
    '''
    Create the minimal necessary data to get the system up and running.
    '''
    default_group = db.Group('test-group')
    default_user = db.User('test-user', default_group)
    default_artist = db.Artist(name='Tool')
    default_album = db.Album(
        name='Lateralus',
        artist=default_artist,
        path='/path/to/song'
    )
    default_song = db.Song(
        localpath='some.mp3',
        artist=default_artist,
        album=default_album,
    )
    dbsession.add(default_song)
    dbsession.add(default_user)
    dbsession.flush()
    yield {
        'default_song': default_song,
    }


def test_something(dbsession, default_data):
    channel_entity = db.Channel('foobar', 'skeleton')
    channel_entity = dbsession.merge(channel_entity)
    channel = chnl.Channel(dbsession, 'foobar')
    channel.queueSong(default_data['default_song'])
