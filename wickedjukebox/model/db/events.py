"""
This module contains DB definitions for tables related to real-world events (a
gathering of people with start- and end-date).
"""

from sqlalchemy.sql.schema import Column, Index
from sqlalchemy.sql.sqltypes import DateTime, Float, Integer, String

from .sameta import Base


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (Index("startdate", "startdate", "enddate"),)

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    startdate = Column(DateTime, nullable=False)
    enddate = Column(DateTime, nullable=False)
    lat = Column(Float)
    lon = Column(Float)
