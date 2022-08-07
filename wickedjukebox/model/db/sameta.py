# type: ignore

"""
This module contains SQL-Alchemy meta-data
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

session_factory = sessionmaker()
Base = declarative_base()
Session = scoped_session(session_factory)


def connect(dsn: str) -> None:
    """
    Establish a database connection and bind the application model to it.
    """
    engine = create_engine(dsn, echo=False)
    Base.metadata.bind = engine
