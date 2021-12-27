# type: ignore
# pylint: disable=no-member, attribute-defined-outside-init
# pylint: disable=too-few-public-methods, invalid-name
#
# SQLAlchemy mapped classes have their members injected by the Base metaclass.
# Pylint does not see those and causes false "no-member" messages. Which is why
# they are disabled in this module. The same goes for variable initialisation.
# Additionally, mapped classes don't necessarily have public methods.
# "invalid-name" is disabled because these variables don't really have the role
# of constants. Renaming them now would just produce even more unnecessary
# git-churn.


import logging
from base64 import b64encode
from datetime import datetime
from os import stat, urandom
from os.path import basename, dirname
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Unicode,
    and_,
    create_engine,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session as TSession
from sqlalchemy.orm import relation, scoped_session, sessionmaker
from sqlalchemy.sql import insert, select, update

from wickedjukebox.config import load_config
from wickedjukebox.logutil import caller_source
from wickedjukebox.model.audiometa import MetaFactory

LOG = logging.getLogger(__name__)
CFG = load_config()
DBURI = CFG.get("database", "dsn")

metadata = MetaData()
engine = create_engine(DBURI, echo=False)
metadata.bind = engine
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

Base = declarative_base(bind=engine)

settingTable = Table(
    "setting", metadata, Column("value", Unicode()), autoload=True
)
song_has_genre = Table("song_has_genre", Base.metadata, autoload=True)
songStandingTable = Table("user_song_standing", Base.metadata, autoload=True)
song_has_tag = Table(
    "song_has_tag",
    Base.metadata,
    Column("song_id", Integer, ForeignKey("song.id")),
    Column("tag", String(32), ForeignKey("tag.label")),
)


# ----------------------------------------------------------------------------
# Mappers
# ----------------------------------------------------------------------------


class Genre(Base):
    __tablename__ = "genre"
    __table_args__ = {
        "extend_existing": True,
        "autoload": True,
    }
    added = Column(DateTime, nullable=False, default=datetime.now)

    def __init__(self, name):
        self.name = name
        self.added = datetime.now()

    def __repr__(self):
        return f"<Genre {self.id} name={repr(self.name)}>"

    @staticmethod
    def by_name(name: str) -> Optional["Genre"]:
        session = Session()
        query = session.query(Genre).filter_by(name=name)
        return query.one_or_none()


class Tag(Base):
    __tablename__ = "tag"
    __table_args__ = {
        "extend_existing": True,
        "autoload": True,
    }

    def __init__(self, label):
        self.label = label
        self.inserted = datetime.now()

    def __repr__(self):
        return "<Tag label=%r>" % (self.label)


class Channel(Base):
    __tablename__ = "channel"
    __table_args__ = {
        "extend_existing": True,
        "autoload": True,
    }
    name = Column(Unicode(32))
    backend = Column(Unicode(64))
    backend_params = Column(Unicode())

    def __init__(self, name, backend, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.backend = backend

    def __repr__(self):
        return f"<Channel {self.id} name={repr(self.name)}>"


class Artist(Base):
    __tablename__ = "artist"
    __table_args__ = {
        "extend_existing": True,
        "autoload": True,
    }
    name = Column(Unicode(128))
    added = Column(DateTime, nullable=False, default=datetime.now)
    albums = relation("Album", backref="artist")
    songs = relation("Song", backref="artist")

    def __init__(self, name):
        self.name = name
        self.added = datetime.now()

    def __repr__(self):
        return f"<Artist {self.id} name={repr(self.name)}>"

    @staticmethod
    def by_name(
        name: str, session: Optional[TSession] = None
    ) -> Optional["Artist"]:
        session = session or Session()
        query = session.query(Artist).filter_by(name=name)
        return query.one_or_none()


class State(Base):
    __tablename__ = "state"
    __table_args__ = {
        "extend_existing": True,
        "autoload": True,
    }

    channel_id = Column(Integer, primary_key=True)
    state = Column(Unicode(64), primary_key=True)

    channel = relation(
        Channel,
        foreign_keys=[channel_id],
        primaryjoin="State.channel_id == Channel.id",
    )

    @classmethod
    def set(cls, statename, value, channel_id=0):
        """
        Saves a state variable into the database

        @param statename: The variable name
        @param value : The value of the state variable
        @param channel_id: (optional) For channel based states, use this to set
                           the channel.
        """

        query = select([State.state])
        query = query.where(State.state == statename)
        query = query.where(State.channel_id == channel_id)
        result = query.execute()
        if result and result.fetchone():
            # the state exists, we need to update it
            query = update(State)
            query = query.values({"value": value, "channel_id": channel_id})
            query = query.where(State.state == statename)
            query = query.where(State.channel_id == channel_id)
            query.execute()
        else:
            # unknown state, store it in the DB
            ins_q = insert(State)
            ins_q = ins_q.values(
                {"state": statename, "value": value, "channel_id": channel_id}
            )
            ins_q.execute()

        if LOG.isEnabledFor(logging.DEBUG):
            source = caller_source()
            LOG.debug(
                "State %r stored with value %r for channel %r " "(from %s:%d)",
                statename,
                value,
                channel_id,
                basename(source[0]),
                source[1],
            )

    @classmethod
    def get(cls, statename, channel_id=0, default=None):
        """
        Retrieve a specific state.

        @param: The variable name
        @param: (optional) The channel id for states bound to a specific
                channel
        @param default: Return this value is the state is not found in the DB.
        @return: The state value
        """
        query = select([State.value])
        query = query.where(State.state == statename)
        query = query.where(State.channel_id == channel_id)
        result = query.execute()
        if result:
            row = result.fetchone()
            if row:
                return row[0]
        if LOG.isEnabledFor(logging.WARNING):
            source = caller_source()
            LOG.warning(
                "State %r not found for channel %r. "
                "Returning %r (from %s:%d)",
                statename,
                channel_id,
                default,
                basename(source[0]),
                source[1],
            )
        ins_q = insert(State)
        ins_q = ins_q.values(
            {"channel_id": channel_id, "state": statename, "value": default}
        )
        ins_q.execute()
        LOG.debug("    Inserted default value into the database!")
        return default


class Album(Base):
    __tablename__ = "album"
    __table_args__ = {
        "extend_existing": True,
        "autoload": True,
    }
    name = Column(Unicode(128))
    type = Column(Unicode(32))
    added = Column(DateTime, nullable=False, default=datetime.now)
    songs = relation("Song", backref="album")

    def __init__(self, name, artist, path):
        self.name = name
        self.artist = artist
        self.path = path
        self.added = datetime.now()

    def __repr__(self):
        return f"<Album {self.id} name={repr(self.name)}>"

    @staticmethod
    def by_name(
        name: str, session: Optional[TSession] = None
    ) -> Optional["Album"]:
        session: TSession = session or Session()
        album = session.query(Album).filter_by(name=name).one_or_none()
        return album


class Song(Base):
    __tablename__ = "song"
    __table_args__ = {
        "extend_existing": True,
        "autoload": True,
    }

    title = Column(Unicode(128))
    localpath = Column(Unicode(255))
    lyrics = Column(Unicode())
    added = Column(DateTime, nullable=False, default=datetime.now)

    channelstat = relation("ChannelStat", backref="song")
    genres = relation(
        Genre,
        secondary=song_has_genre,
        backref="songs",
        primaryjoin="Song.id == song_has_genre.c.song_id",
        secondaryjoin="song_has_genre.c.genre_id == Genre.id",
    )

    tags = relation(Tag, secondary=song_has_tag, backref="songs")

    def __init__(self, localpath: str) -> None:
        self.localpath = localpath
        self.added = datetime.now()

    def __repr__(self):
        return "<Song id={!r} artist_id={!r} title={!r} path={!r}>".format(
            self.id,
            self.artist_id,
            self.title,
            self.localpath,
        )

    @staticmethod
    def by_filename(session: TSession, filename: str) -> Optional["Song"]:
        """
        Retrieve a song from the database using the local filename as key
        """
        song = session.query(Song).filter_by(localpath=filename).one_or_none()
        return song

    @staticmethod
    def random(session: TSession) -> Optional["Song"]:
        """
        Retrieve a song from the database using the local filename as key
        """
        query = session.query(Song).order_by(func.rand())
        song = query.first()
        return song

    @staticmethod
    def smart_random(session: TSession, channel_name: str) -> Optional["Song"]:
        """
        Retrieve a song using a smart guess based on play statistics and active
        listeners.
        """
        from wickedjukebox.core.smartfind import find_song

        song = find_song(session, channel_name)
        return song

    def update_metadata(self) -> None:
        """
        Scans a file on the disk and loads the metadata from that file

        :param localpath: The absolute path to the file
        :param encoding: The file system encoding
        """
        localpath = self.localpath
        LOG.debug("Extracting metadata from %r", localpath)

        audiometa = MetaFactory.create(localpath)
        dirname_ = dirname(localpath)

        artist = Artist.by_name(audiometa["artist"])
        if not artist:
            artist = Artist(audiometa["artist"])
        self.artist = artist

        album = Album.by_name(audiometa["album"])
        if not album:
            album = Album(
                audiometa["album"],
                artist,
                dirname_,
            )
        self.album = album

        self.genres = []
        if audiometa["genres"] is not None:
            for genre_name in audiometa["genres"]:
                genre = Genre.by_name(genre_name)
                if not genre:
                    genre = Genre(genre_name)
                self.genres.append(genre)
        self.title = audiometa["title"]
        self.duration = audiometa["duration"]
        self.bitrate = audiometa["bitrate"]
        self.track_no = audiometa["track_no"]

        release_date = audiometa["release_date"]
        if release_date:
            self.year = release_date.year

        self.filesize = stat(localpath).st_size

        self.lastScanned = datetime.now()


class QueueItem(Base):
    __tablename__ = "queue"
    __table_args__ = {
        "extend_existing": True,
        "autoload": True,
    }
    added = Column(DateTime, nullable=False, default=datetime.now)
    song = relation(Song)

    def __init__(self):
        self.added = datetime.now()

    def __repr__(self):
        return "<QueueItem id={!r} position={!r} song_id={!r}>".format(
            self.id,
            self.position,
            self.song_id,
        )

    @staticmethod
    def next(session: TSession, channel_name: str) -> Optional["QueueItem"]:
        """
        Return the next song on the queue or None if the queue is empty
        """
        channel = (
            session.query(Channel.id).filter(Channel.name == channel_name).one()
        )
        query = session.query(QueueItem).filter(
            and_(QueueItem.position == 0, QueueItem.channel_id == channel.id)
        )
        output = query.one_or_none()
        return output

    @staticmethod
    def advance(session: TSession, channel_name: str) -> None:
        """
        Advance the queue by one song. Keeps a "history" of 10 songs
        """
        channel = (
            session.query(Channel.id).filter(Channel.name == channel_name).one()
        )
        session.query(QueueItem).filter(
            QueueItem.channel_id == channel.id
        ).update({QueueItem.position: QueueItem.position - 1})
        session.query(QueueItem).filter(QueueItem.position < -10).delete()


class DynamicPlaylist(Base):
    __tablename__ = "dynamicPlaylist"
    __table_args__ = {
        "extend_existing": True,
        "autoload": True,
    }
    label = Column(Unicode(64))
    query = Column(Unicode())

    def __repr__(self):
        return "<DynamicPlaylist %s>" % (self.id)


class ChannelStat(Base):
    __tablename__ = "channel_song_data"
    __table_args__ = {
        "extend_existing": True,
        "autoload": True,
    }

    def __init__(self, song_id, channel_id):
        self.song_id = song_id
        self.channel_id = channel_id


class User(Base):
    __tablename__ = "users"
    __table_args__ = {
        "extend_existing": True,
        "autoload": True,
    }
    added = Column(DateTime, nullable=False, default=datetime.now)
    group = relation("Group", backref="users")

    def __init__(self, username, group, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = username
        self.cookie = ""
        self.password = b64encode(urandom(20)).decode("ascii")
        self.fullname = "default user"
        self.email = ""
        self.proof_of_life = datetime.now()
        self.proof_of_listening = None
        self.IP = ""
        self.credits = 0
        self.group = group
        self.picture = ""
        self.lifetime = 0

    def __repr__(self):
        return "<User %d %r>" % (self.id, self.username)


class Group(Base):
    __tablename__ = "groups"
    __table_args__ = {
        "extend_existing": True,
        "autoload": True,
    }

    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title

    def __repr__(self):
        return "<Group %d %r>" % (self.id, self.title)
