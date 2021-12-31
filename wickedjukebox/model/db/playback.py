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
This module contains DB definitions for tables used to steer the music playback
"""
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    and_,
    text,
)
from sqlalchemy.orm import Session as TSession
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKeyConstraint

from .sameta import Base


class Channel(Base):
    __tablename__ = "channel"
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    public = Column(Boolean, nullable=False, server_default=text("1"))
    backend = Column(String(64), nullable=False)
    backend_params = Column(Text())
    ping = Column(DateTime)
    active = Column(Boolean, nullable=False, server_default=text("0"))
    status = Column(Integer)

    def __init__(self, name, backend, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.backend = backend

    def __repr__(self):
        return f"<Channel {self.id} name={repr(self.name)}>"


class State(Base):
    __tablename__ = "state"
    __table_args__ = (Index("channel_id", "channel_id", "state", unique=True),)

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, nullable=False)
    state = Column(String(64), nullable=False)
    value = Column(String(255))

    # XXX channel = relation(
    # XXX     Channel,
    # XXX     foreign_keys=[channel_id],
    # XXX     primaryjoin="State.channel_id == Channel.id",
    # XXX )

    @classmethod
    def set(cls, statename, value, channel_id=0):
        """
        Saves a state variable into the database

        :param statename: The variable name
        :param value: The value of the state variable
        :param channel_id: (optional) For channel based states, use this to set
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

        :param: The variable name
        :param: (optional) The channel id for states bound to a specific
            channel
        :param default: Return this value is the state is not found in the DB.
        :return: The state value
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


class QueueItem(Base):
    __tablename__ = "queue"
    __table_args__ = (
        Index("channel_id", "channel_id", unique=False),
        Index("position", "position", unique=False),
        Index("song_id", "song_id", unique=False),
        Index("user_id", "user_id", unique=False),
        ForeignKeyConstraint(
            ["song_id"],
            ["song.id"],
            name="queue_ibfk_2",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="queue_ibfk_1",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ["channel_id"],
            ["channel.id"],
            name="queue_ibfk_3",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )
    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, nullable=False)
    user_id = Column(Integer)
    channel_id = Column(Integer, nullable=False)
    position = Column(Integer, server_default=text("0"))
    added = Column(DateTime, nullable=False)

    channel = relationship("Channel")
    song = relationship("Song")
    user = relationship("User")

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
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer)
    group_id = Column(Integer, nullable=False)
    probability = Column(
        Float,
        nullable=False,
        comment="Probability at which a song is picked from the playlisy (0.0-1.0)",
    )
    label = Column(String(64))
    query = Column(Text())

    def __repr__(self):
        return "<DynamicPlaylist %s>" % (self.id)


class RandomSongsToUse(Base):
    __tablename__ = "randomSongsToUse"
    __table_args__ = (Index("used", "used", unique=False),)

    id = Column(Integer, primary_key=True)
    used = Column(Boolean, nullable=False, server_default=text("0"))
    in_string = Column(String(255), nullable=False)
