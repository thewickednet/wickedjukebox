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


"""
This module contains DB definitions for table related to the song library
"""

import enum
import logging
from datetime import datetime
from os import stat
from os.path import dirname
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Session as TSession
from sqlalchemy.orm import relation, relationship
from sqlalchemy.sql.schema import ForeignKeyConstraint

from wickedjukebox.model.audiometa import MetaFactory

from .sameta import Base, Session

LOG = logging.getLogger(__name__)


class StandingEnum(enum.Enum):
    LOVE = "love"
    HATE = "hate"


class Genre(Base):
    __tablename__ = "genre"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
    added = Column(DateTime, nullable=False)

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
    id = Column(Integer, primary_key=True)
    label = Column(String(32), nullable=False, unique=True)
    inserted = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("current_timestamp()"),
    )
    modified = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("'0000-00-00 00:00:00'"),
    )

    def __init__(self, label):
        self.label = label
        self.inserted = datetime.now()

    def __repr__(self):
        return "<Tag label=%r>" % (self.label)


class Artist(Base):
    __tablename__ = "artist"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
    country = Column(String(16))
    summary = Column(Text())
    bio = Column(Text())
    website = Column(String(255))
    wikipage = Column(String(255))
    lastfm_mbid = Column(String(64))
    lastfm_url = Column(String(255))
    added = Column(DateTime)
    photo = Column(String(255))

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


class Album(Base):
    __tablename__ = "album"
    __table_args__ = (
        Index("artist_id", "artist_id", unique=False),
        Index("name", "name", unique=False),
        Index("type", "type", unique=False),
    )
    id = Column(Integer, primary_key=True)
    artist_id = Column(
        Integer,
        ForeignKey("artist.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    name = Column(String(128), index=True)
    release_date = Column(Date)
    added = Column(DateTime, nullable=False)
    downloaded = Column(Integer, nullable=False, server_default=text("0"))
    type = Column(String(32), server_default=text("'album'"))
    path = Column(String(255), nullable=False, unique=True)
    coverart = Column(String(255))
    lastfm_mbid = Column(String(255))
    lastfm_url = Column(String(255))

    artist = relationship("Artist", backref="albums")

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
    __table_args__ = (
        Index("album_id", "album_id", unique=False),
        Index("artist_id", "artist_id", unique=False),
        Index("broken", "broken", unique=False),
        Index("title", "title", unique=False),
        ForeignKeyConstraint(
            ["artist_id"],
            ["artist.id"],
            name="song_ibfk_1",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ["album_id"],
            ["album.id"],
            name="song_ibfk_2",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
    )

    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, nullable=False)
    album_id = Column(Integer)
    track_no = Column(Integer)
    title = Column(String(128))
    duration = Column(Float(asdecimal=True))
    year = Column(Integer)
    localpath = Column(String(255), nullable=False, unique=True)
    downloaded = Column(Integer, server_default=text("0"))
    lastScanned = Column(DateTime)
    bitrate = Column(Integer)
    filesize = Column(Integer)
    checksum = Column(String(14))
    lyrics = Column(Text())
    broken = Column(Boolean, server_default=text("0"))
    dirty = Column(Boolean, server_default=text("0"))
    added = Column(DateTime, nullable=False)
    available = Column(Boolean, server_default=text("1"))
    coverart = Column(String(255))
    lastfm_mbid = Column(String(255))
    lastfm_url = Column(String(255))

    album = relationship("Album")
    artist = relationship("Artist")

    # XXX channelstat = relation("ChannelStat", backref="song")
    # XXX genres = relation(
    # XXX     Genre,
    # XXX     secondary=song_has_genre,
    # XXX     backref="songs",
    # XXX     primaryjoin="Song.id == song_has_genre.c.song_id",
    # XXX     secondaryjoin="song_has_genre.c.genre_id == Genre.id",
    # XXX )

    tags = relation(Tag, secondary="song_has_tag", backref="songs")

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
        if session.bind is None:
            LOG.warning("No DB is bound to this session. Returning None!")
            return None
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


class Collection(Base):
    __tablename__ = "collection"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String(32), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("0"))


class CollectionhasSong(Base):
    __tablename__ = "collection_has_song"
    __table_args__ = (
        Index("collection_id", "collection_id", "song_id", unique=True),
    )

    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, nullable=False)
    song_id = Column(Integer, nullable=False)
    position = Column(Integer)
    last_played = Column(DateTime)


class Country(Base):
    __tablename__ = "country"

    country_code = Column(
        String(16),
        primary_key=True,
        server_default=text("''"),
    )
    country_name = Column(
        String(100),
        nullable=False,
        server_default=text("''"),
    )


class Playlist(Base):
    __tablename__ = "playlist"
    __table_args__ = (Index("user_id", "user_id", "probability"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String(32), nullable=False)
    probability = Column(Float)


class PlaylistHasSong(Base):
    __tablename__ = "playlist_has_song"

    playlist_id = Column(Integer, primary_key=True, nullable=False)
    song_id = Column(Integer, primary_key=True, nullable=False)


class SongHasTag(Base):
    __tablename__ = "song_has_tag"
    __table_args__ = (
        Index("song_id", "song_id", "tag_id", unique=True),
        ForeignKeyConstraint(
            ["song_id"],
            ["song.id"],
            name="song_has_tag_song_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ["tag_id"],
            ["tag.id"],
            name="song_has_tag_tag_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, nullable=False)
    tag_id = Column(Integer, nullable=False)


class UserSongStanding(Base):
    __tablename__ = "user_song_standing"
    __table_args__ = (
        Index("user_song_id", "user_id", "song_id", unique=True),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="user_song_standing_user_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ["song_id"],
            ["song.id"],
            name="user_song_standing_song_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        nullable=False,
    )
    song_id = Column(
        Integer,
        nullable=False,
    )
    standing = Column(Enum(StandingEnum), nullable=False)
    inserted = Column(
        DateTime(timezone=True), server_default=text("current_timestamp()")
    )


class SongHasGenre(Base):
    __tablename__ = "song_has_genre"
    __table_args__ = (
        Index("song_id_2", "song_id", "genre_id", unique=True),
        Index("song_id", "genre_id", unique=False),
        Index("genre_id", "song_id", unique=False),
        ForeignKeyConstraint(
            ["song_id"],
            ["song.id"],
            name="song_has_genre_ibfk_2",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ["genre_id"],
            ["genre.id"],
            name="song_has_genre_ibfk_1",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    id = Column(Integer, primary_key=True)
    song_id = Column(
        Integer,
        nullable=False,
    )
    genre_id = Column(
        Integer,
        nullable=False,
    )

    genre = relationship("Genre")
    song = relationship("Song")
