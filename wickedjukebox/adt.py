"""
Collection of abstract data types
"""

from typing import NamedTuple


class Song(NamedTuple):
    artist: str
    album: str
    title: str
    filename: str
