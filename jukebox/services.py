# -*- coding: utf-8 -*-

from .core import Service
from .models import Artist, Album, Song


class ArtistService(Service):
    __model__ = Artist


class SongService(Service):
    __model__ = Song


class AlbumService(Service):
    __model__ = Album


artist = ArtistService()
song = SongService()
album = AlbumService()
