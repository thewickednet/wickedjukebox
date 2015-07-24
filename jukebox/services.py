# -*- coding: utf-8 -*-

from .core import Service
from .models import Artist, Album, Song, Queue, Channel, User, State


class ArtistService(Service):
    __model__ = Artist


class SongService(Service):
    __model__ = Song


class AlbumService(Service):
    __model__ = Album


class ChannelService(Service):
    __model__ = Channel


class QueueService(Service):
    __model__ = Queue


class UserService(Service):
    __model__ = User


class StateService(Service):
    __model__ = State


artist = ArtistService()
song = SongService()
album = AlbumService()
channel = ChannelService()
queue = QueueService()
user = UserService()
state = StateService()
