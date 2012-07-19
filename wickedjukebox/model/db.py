"""
Database model
"""
import logging
from datetime import datetime

from sqlalchemy import (
    func,
    Table,
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
    relationship,
    sessionmaker)

from sqlalchemy.ext.declarative import declarative_base

BASE = declarative_base()
SESSION = sessionmaker()
META = MetaData()


artist_in_band_table = Table('artist_in_band', BASE.metadata,
    Column('artist_id', Integer, ForeignKey(
        'artist.id', onupdate='CASCADE', ondelete='CASCADE'
        ), nullable=False),
    Column('band_id', Integer, ForeignKey(
        'band.id', onupdate='CASCADE', ondelete='CASCADE'
        ), nullable=False),
    PrimaryKeyConstraint('artist_id', 'band_id'))


class TimestampMixin(object):

    inserted = Column(DateTime, nullable=False,
        server_default=func.now(),
        default=func.now())

    updated = Column(DateTime, nullable=False,
        onupdate=datetime.now,
        default=func.now())


def init(uri):
    BASE.metadata.bind = create_engine(uri, echo=True)


class MusicalWork(TimestampMixin, BASE):
    """
    A "musical work" is a composition.
    """
    __tablename__ = 'musical_work'
    log = logging.getLogger('{0}.MusicalWork'.format(__name__))
    id = Column(Integer, primary_key=True)
    title = Column(Unicode)

    def __init__(self, title):
        self.title = title

    @staticmethod
    def get_or_add(session, title):
        MusicalWork.log.debug(u'Retrieving {0}'.format(title))
        q = session.query(MusicalWork)
        q = q.filter_by(title=title)
        result = q.first()
        if not result:
            MusicalWork.log.info(u'MusicalWork {0} did '
                u'not exist. Adding it to the DB'.format(title))
            result = MusicalWork(title)
            session.add(result)
        return result

    @staticmethod
    def get(session, id):
        q = session.query(MusicalWork)
        q = q.filter_by(id=id)
        result = q.first()
        if not result:
            raise ValueError('No musical work with id {0} found!'.format(id))
        return result


class MusicalManifestation(TimestampMixin, BASE):
    """
    A "musical manifestation" is a musical work performed by a band. The same
    musical work may be performed by multiple artists/bands. Hence the
    separation between these two.
    """
    __tablename__ = 'musical_manifestation'
    log = logging.getLogger('{0}.MusicalManifestation'.format(__name__))

    id = Column(Integer, primary_key=True)
    duration = Column(Integer)
    release_date = Column(Date)
    filename = Column(Unicode)
    last_scanned = Column(DateTime)
    band_id = Column('band', Integer,
        ForeignKey('band.id',  onupdate="CASCADE", ondelete="CASCADE"))
    musical_work_id = Column('musical_work', Integer,
        ForeignKey('musical_work.id', onupdate="CASCADE", ondelete="CASCADE"))

    band = relationship('Band', backref='musical_manifestations')
    musical_work = relationship('MusicalWork', backref='musical_manifestations')

    def __init__(self, band, musical_work):
        self.band = band
        self.musical_work = musical_work

    @staticmethod
    def get_or_add(session, band, musical_work):

        MusicalManifestation.log.debug(u'Retrieving {0} - {1}'.format(
            band, musical_work))
        q = session.query(MusicalManifestation)
        q = q.filter_by(band=band)
        q = q.filter_by(musical_work=musical_work)
        result = q.first()
        if not result:
            MusicalManifestation.log.info(u'MusicalManifestation {0} - {1} '
                u'did not exist. Adding it to the '
                u'DB'.format(band, musical_work))
            result = MusicalManifestation(band, musical_work)
            session.add(result)
        result.band = band
        return result


class Band(TimestampMixin, BASE):
    __tablename__ = 'band'
    log = logging.getLogger('{0}.Band'.format(__name__))
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)

    artists = relationship('Artist', secondary=artist_in_band_table,
            backref='bands')

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


class Artist(TimestampMixin, BASE):
    __tablename__ = 'artist'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    birthdate = Column(Date)
