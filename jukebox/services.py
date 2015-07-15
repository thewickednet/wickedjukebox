# -*- coding: utf-8 -*-

from .core import Service
from .models import Artist


class ArtistService(Service):
    __model__ = Artist


artist = ArtistService()