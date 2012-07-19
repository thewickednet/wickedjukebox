"""
Database model
"""
import logging
from datetime import datetime

from sqlalchemy import (
    func,
    Table,
    String,
    Integer,
    Unicode,
    Column,
    ForeignKey,
    PrimaryKeyConstraint,
    Date,
    DateTime,
    create_engine,
    MetaData)

from sqlalchemy.orm import (
    mapper,
    sessionmaker)

SESSION = sessionmaker()
META = MetaData()

def init(uri):
    META.bind = create_engine(uri, echo=True)

musical_work_table = Table('musical_work', META,
    Column('id', Integer, primary_key=True),
    Column('title', Unicode)
    )

# Songs
musical_manifestation_table = Table('musical_manifestation', META,
    Column('id', Integer, primary_key=True),
    Column('duration', Integer),
    Column('release_date', Date),
    Column('filename', Unicode),
    Column('last_scanned', DateTime),
    Column('inserted', DateTime, nullable=False,
        server_default=func.now(),
        default=func.now()),
    Column('updated', DateTime, nullable=False,
        onupdate=datetime.now,
        default=func.now()),
    Column('band', Integer,
        ForeignKey('band.id',  onupdate="CASCADE", ondelete="CASCADE")),
    Column('song', Integer,
        ForeignKey('song.id', onupdate="CASCADE", ondelete="CASCADE"))
    )


band_table = Table('band', META,
    Column('id', Integer, primary_key=True),
    Column('name', Unicode))


artist_table = Table('artist', META,
    Column('id', Integer, primary_key=True),
    Column('name', Unicode),
    Column('birthdate', Date))


artist_band_table = Table('artist_in_band', META,
    Column('artist_id', Integer, ForeignKey(
        'artist.id', onupdate='CASCADE', ondelete='CASCADE'
        ), nullable=False),
    Column('band_id', Integer, ForeignKey(
        'band.id', onupdate='CASCADE', ondelete='CASCADE'
        ), nullable=False),
    PrimaryKeyConstraint('artist_id', 'band_id'))


class Song(object):
    log = logging.getLogger('{0}.Song'.format(__name__))

    def __init__(self, title):
        self.title = title

    @staticmethod
    def get_or_add(session, title):
        Song.log.debug(u'Retrieving {0}'.format(title))
        q = session.query(Song)
        q = q.filter_by(title=title)
        result = q.first()
        if not result:
            Song.log.info(u'Song {0} did not exist. '
                u'Adding it to the DB'.format(title))
            result = Song(title)
            session.add(result)
        return result


class Artist(object):
    pass


class Band(object):

    log = logging.getLogger('{0}.Band'.format(__name__))

    def __init__(self, name):
        self.name = name

    @staticmethod
    def get_or_add(session, name):
        Band.log.debug(u'Retrieving {0}'.format(name))
        q = session.query(Band)
        q = q.filter_by(name=name)
        result = q.first()
        if not result:
            Band.log.info(u'Band {0} did not exist. '
                u'Adding it to the DB'.format(name))
            result = Band(name)
            session.add(result)
        return result


class PerformedSong(object):
    log = logging.getLogger('{0}.PerformedSong'.format(__name__))


mapper(Song, song_table)
mapper(Artist, artist_table)
mapper(Band, band_table)
mapper(PerformedSong, performed_song_table)
