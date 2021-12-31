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
This module contains DB definitions for tables related to core application
settings.
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


class Setting(Base):
    __tablename__ = "setting"
    __table_args__ = (
        Index("var", "var", unique=False),
        Index("channel_id", "channel_id", unique=False),
        Index("user_id", "user_id", unique=False),
        Index("var_2", "var", "channel_id", "user_id", unique=True),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="setting_ibfk_1",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["channel_id"],
            ["channel.id"],
            name="setting_ibfk_2",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )
    id = Column(Integer, nullable=False, primary_key=True)
    var = Column(String(32), nullable=False)
    value = Column(String())
    channel_id = Column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )
    user_id = Column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )


class SettingText(Base):
    __tablename__ = "setting_text"

    var = Column(String(32), nullable=False, primary_key=True)
    text_en = Column(Text, nullable=False)
