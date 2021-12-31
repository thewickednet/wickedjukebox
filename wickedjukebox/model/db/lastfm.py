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
This module contains DB definitions for tables related to LastFM interaction
"""


from sqlalchemy import DateTime, Index, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKeyConstraint

from .sameta import Base


class LastfmQueue(Base):
    __tablename__ = "lastfm_queue"
    __table_args__ = (
        Index("song_id", "song_id", unique=False),
        ForeignKeyConstraint(
            ["song_id"],
            ["song.id"],
            name="lastfm_queue_ibfk_2",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )

    queue_id = Column(Integer, primary_key=True)
    song_id = Column(Integer, nullable=False)
    time_played = Column(DateTime, nullable=False)
    time_started = Column(DateTime, nullable=False)

    song = relationship("Song")
