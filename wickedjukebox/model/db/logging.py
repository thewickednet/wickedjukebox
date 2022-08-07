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
This module contains DB definitions for tables used in application logging
"""


from sqlalchemy import Column, DateTime, String, Table, Text, text

from .sameta import Base

t_log = Table(
    "log",
    Base.metadata,
    Column("priority", String(32), nullable=False),
    Column("message", Text, nullable=False),
    Column(
        "date",
        DateTime(timezone=True),
        nullable=False,
        server_default=text(
            "current_timestamp() ON UPDATE current_timestamp()"
        ),
    ),
)
