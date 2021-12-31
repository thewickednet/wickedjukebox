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
This module contains DB definitions for statistics
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
    Table,
    Text,
    text,
)
from sqlalchemy.orm import Session as TSession
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKeyConstraint

from .sameta import Base

t_user_album_stats = Table(
    "user_album_stats",
    Base.metadata,
    Column("user_id", Integer, nullable=False),
    Column("album_id", Integer, nullable=False),
    Column("when", DateTime, nullable=False),
    Index("album_id", "album_id", unique=False),
    Index("user_id", "user_id", unique=False),
    ForeignKeyConstraint(
        ["user_id"],
        ["users.id"],
        name="user_album_stats_ibfk_1",
        ondelete="CASCADE",
        onupdate="CASCADE",
    ),
    ForeignKeyConstraint(
        ["album_id"],
        ["album.id"],
        name="user_album_stats_ibfk_2",
        ondelete="CASCADE",
        onupdate="CASCADE",
    ),
)


class UserSongStat(Base):
    __tablename__ = "user_song_stats"
    __table_args__ = (
        Index("song_id", "song_id", unique=False),
        Index("user_id", "user_id", unique=False),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="user_song_stats_ibfk_1",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ["song_id"],
            ["song.id"],
            name="user_song_stats_ibfk_2",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    user_id = Column(
        Integer,
        primary_key=True,
        nullable=False,
    )
    song_id = Column(
        Integer,
        primary_key=True,
        nullable=False,
    )
    when = Column(DateTime, primary_key=True, nullable=False)

    song = relationship("Song")
    user = relationship("User")


class ChannelAlbumDatum(Base):
    __tablename__ = "channel_album_data"
    __table_args__ = (
        Index("channel_id_2", "channel_id", "album_id", unique=True),
    )

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, nullable=False)
    album_id = Column(Integer, nullable=False)
    played = Column(Integer, nullable=False, server_default=text("0"))


class ChannelStat(Base):
    __tablename__ = "channel_song_data"
    __table_args__ = (
        Index("channel_id_2", "channel_id", "song_id", unique=True),
        Index("song_id", "song_id", unique=False),
        Index("channel_id", "channel_id", unique=False),
    )

    id = Column(Integer, primary_key=True)
    channel_id = Column(
        ForeignKey("channel.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    song_id = Column(
        ForeignKey("song.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    played = Column(Integer, nullable=False, server_default=text("0"))
    voted = Column(Integer, nullable=False, server_default=text("0"))
    skipped = Column(Integer, nullable=False, server_default=text("0"))
    lastPlayed = Column(DateTime)
    cost = Column(Integer, server_default=text("5"))

    channel = relationship("Channel")
    song = relationship("Song")

    def __init__(self, song_id, channel_id):
        self.song_id = song_id
        self.channel_id = channel_id
