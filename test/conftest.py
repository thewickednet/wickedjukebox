import pytest
import wickedjukebox.demon.dbmodel as db


@pytest.fixture
def default_data(dbsession, transaction):
    """
    Create the minimal necessary data to get the system up and running.
    """
    dbsession.bind = transaction
    default_channel = db.Channel("test-channel", "mpd")

    default_group = db.Group("test-group")
    default_user = db.User("test-user", default_group)
    default_artist = db.Artist(name="Tool")
    default_album = db.Album(
        name="Lateralus", artist=default_artist, path="/path/to/song"
    )
    default_song = db.Song(
        localpath="some.mp3",
    )
    default_song.artist = default_artist
    default_song.album = default_album
    default_song.title = "title"

    dbsession.add(default_channel)
    dbsession.add(default_song)
    dbsession.add(default_user)
    dbsession.flush()

    dbsession.execute(
        db.songStandingTable.insert().values(
            {
                "user_id": default_user.id,
                "song_id": default_song.id,
                "standing": "love",
            }
        )
    )

    yield {
        "default_artist": default_artist,
        "default_album": default_album,
        "default_song": default_song,
        "default_user": default_user,
        "default_channel": default_channel,
    }
