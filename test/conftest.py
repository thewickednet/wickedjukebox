import pytest
import wickedjukebox.demon.dbmodel as db
from pytest_sqlalchemy import dbsession


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

    dbsession.execute(db.songStandingTable.insert().values({
        'user_id': default_user.id,
        'song_id': default_song.id,
        'standing': 'love',
    }))

    yield {
        'default_song': default_song,
        'default_user': default_user,
    }
