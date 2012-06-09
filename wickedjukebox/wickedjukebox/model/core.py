from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import (Column,
        Integer,
        String,
        ForeignKey,
        Unicode,
        text,
        Sequence,
        Table,
        Date)

Base = declarative_base()

album_songs = Table('album_songs', Base.metadata,
        Column('album_id', Integer, ForeignKey('album.id'), primary_key=True),
        Column('song_id', Integer, ForeignKey('song.id'), primary_key=True)
        )

class PerformsOn(Base):
    """
    An artist performs on a song, fulfilling a specific role (f. ex.:
    "Drummer", "Singer", "Composer", "Arranger", ...)

    .. note:: It's debatable wether "Interpreter" belongs here. You could
              consider one artist as interpreter, but also the whole
              artist-constellation. Most likely the constellation is
              responsible for interpreting a specific song!

    .. warning:: Do *not* use this as a ``secondary`` table elsewhere!
                 See (http://docs.sqlalchemy.org/en/latest/orm/relationships.html#association-object)
    """

    __tablename__ = 'performs_on'
    artist_id = Column(Integer, ForeignKey('artist.id'), primary_key=True)
    song_id = Column(Integer, ForeignKey('song.id'), primary_key=True)
    role = String()
    song = relationship('Song', backref="artist_assocs")


class Artist(Base):
    __tablename__ = 'artist'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    songs = relationship('PerformsOn', backref="artist")


class Constellation(Base):
    "Bands as SCD"
    __tablename__ = 'constellation'
    id = Column(Integer, primary_key=True)
    natural_id = Column(Integer, Sequence('constellation_natual_id_seq'),
            server_default=text("nextval('constellation_natual_id_seq')"))
    name = Column(Unicode)
    valid_from = Column(Date)
    valid_until = Column(Date)


class Album(Base):
    "Relesed album"
    __tablename__ = "album"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    release_date = Column(Date)
    songs = relationship('Song', secondary=album_songs, backref='albums')


class Song(Base):
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True)

    # The "simple" name of the song
    name = Column(Unicode)

    # The song "variant" (f. ex.: "Club Mix" or "Instrumental")
    variant = Column(Unicode)

