# type: ignore
# pylint: disable=redefined-outer-name
import pytest
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker

import wickedjukebox.model.db.sameta as sameta
from alembic import command
from alembic.config import Config
from wickedjukebox.config import Config as WJConfig
from wickedjukebox.config import ConfigKeys
from wickedjukebox.model.db.auth import Group, User
from wickedjukebox.model.db.library import Album, Artist, Song, UserSongStanding
from wickedjukebox.model.db.playback import Channel


def run_migrations(script_location: str, dsn: str) -> None:
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_cfg.set_main_option("sqlalchemy.url", dsn)
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session")
def db_connection():
    config = WJConfig()
    dsn = config.get(ConfigKeys.DSN)
    engine = create_engine(dsn)
    return engine.connect()


def seed_database():
    pass


@pytest.fixture(scope="session")
def setup_database(db_connection):
    sameta.Base.metadata.bind = db_connection
    config = WJConfig()
    dsn = config.get(ConfigKeys.DSN)
    run_migrations("alembic", dsn)
    seed_database()
    yield


@pytest.fixture
def dbsession(setup_database, db_connection):
    # pylint: disable=unused-argument
    transaction = db_connection.begin()
    try:
        yield scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=db_connection)
        )
    finally:
        transaction.rollback()


@pytest.fixture
def default_data(dbsession):
    """
    Create the minimal necessary data to get the system up and running.
    """
    dbsession.execute("DELETE FROM song")
    dbsession.flush()
    default_channel = Channel("test-channel", "mpd")

    default_group = Group("test-group")
    default_user = User("test-user", default_group)
    default_artist = Artist(name="Tool")
    default_album = Album(
        name="Lateralus", artist=default_artist, path="/path/to/song"
    )
    default_song = Song(localpath="some.mp3")
    default_song.artist = default_artist
    default_song.album = default_album
    default_song.title = "title"
    default_song.duration = 300

    dbsession.add(default_channel)
    dbsession.add(default_song)
    dbsession.add(default_user)
    dbsession.flush()

    example_standing = UserSongStanding(
        user_id=default_user.id, song_id=default_song.id, standing="love"
    )
    dbsession.add(example_standing)

    yield {
        "default_artist": default_artist,
        "default_album": default_album,
        "default_song": default_song,
        "default_user": default_user,
        "default_channel": default_channel,
    }
