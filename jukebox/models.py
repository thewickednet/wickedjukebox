# -*- coding: utf-8 -*-

from flask_login import UserMixin

from .core import db
from .helpers import JsonSerializer
import hashlib

class ArtistJsonSerializer(JsonSerializer):
    __json_hidden__ = []


class Artist(ArtistJsonSerializer, db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(128))
    country = db.Column(db.String(16))
    summary = db.Column(db.Text())
    bio = db.Column(db.Text())
    added = db.Column(db.DateTime())

    def __str__(self):
        return "%s (%s)" % (self.name, self.id)


class SongJsonSerializer(JsonSerializer):
    __json_hidden__ = ['localpath', 'checksum']


class Song(SongJsonSerializer, db.Model):
    __tablename__ = 'song'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(128))
    duration = db.Column(db.Float())
    track_no = db.Column(db.Integer())
    year = db.Column(db.Integer())
    bitrate = db.Column(db.Integer())
    localpath = db.Column(db.String(255))
    downloaded = db.Column(db.Integer())
    filesize = db.Column(db.Integer())
    checksum = db.Column(db.String(14))
    lyrics = db.Column(db.Text())
    added = db.Column(db.DateTime())
    artist_id = db.Column(db.Integer(), db.ForeignKey('artist.id'))
    album_id = db.Column(db.Integer(), db.ForeignKey('album.id'))
    artist = db.relationship("Artist")

    def __str__(self):
        return "%s (%s)" % (self.title, self.id)


class AlbumJsonSerializer(JsonSerializer):
    __json_hidden__ = ['localpath', 'checksum']


class Album(AlbumJsonSerializer, db.Model):
    __tablename__ = 'album'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(128))
    release_date = db.Column(db.Integer())
    type = db.Column(db.String(32))
    added = db.Column(db.DateTime())
    artist_id = db.Column(db.Integer(), db.ForeignKey('artist.id'))

    def __str__(self):
        return "%s (%s)" % (self.name, self.id)


class UserJsonSerializer(JsonSerializer):
    __json_hidden__ = ['password']


class User(UserMixin, UserJsonSerializer, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(32))
    password = db.Column(db.String(32))
    fullname = db.Column(db.String(64))
    email = db.Column(db.String(128))
    credits = db.Column(db.Integer())
    group_id = db.Column(db.Integer())
    downloads = db.Column(db.Integer())
    votes = db.Column(db.Integer())
    skips = db.Column(db.Integer())
    selects = db.Column(db.Integer())
    added = db.Column(db.DateTime())
    proof_of_life = db.Column(db.DateTime())
    proof_of_listening = db.Column(db.DateTime())
    picture = db.Column(db.String(255))
    lifetime = db.Column(db.Integer())
    channel_id = db.Column(db.Integer())
    pinnedIp = db.Column(db.String(32))

    def __str__(self):
        return "%s (%s)" % (self.fullname, self.id)

    def check_password(self, data):
        password_hash = hashlib.md5(data.encode('utf8')).hexdigest()
        if password_hash == self.password:
            return True
        return False


class GroupJsonSerializer(JsonSerializer):
    __json_hidden__ = ['']


class Group(GroupJsonSerializer, db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(32))
    admin = db.Column(db.Integer())
    nocredits = db.Column(db.Integer())
    queue_skip = db.Column(db.Integer())
    queue_remove = db.Column(db.Integer())
    queue_add = db.Column(db.Integer())


class QueueJsonSerializer(JsonSerializer):
    __json_hidden__ = ['']


class Queue(QueueJsonSerializer, db.Model):
    __tablename__ = 'queue'

    id = db.Column(db.Integer(), primary_key=True)
    song_id = db.Column(db.Integer(), db.ForeignKey('song.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    channel_id = db.Column(db.Integer(), db.ForeignKey('channel.id'))
    position = db.Column(db.Integer())
    added = db.Column(db.DateTime())
    song = db.relationship("Song", uselist=False)


class ChannelJsonSerializer(JsonSerializer):
    __json_hidden__ = ['']


class Channel(ChannelJsonSerializer, db.Model):
    __tablename__ = 'channel'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(32))
    public = db.Column(db.Integer())
    backend = db.Column(db.String(64))
    backend_params = db.Column(db.Text())
    ping = db.Column(db.DateTime())
    active = db.Column(db.Integer())
    status = db.Column(db.Integer())

    def __str__(self):
        return "%s (%s)" % (self.name, self.id)


class State(db.Model):
    __tablename__ = 'state'

    channel_id = db.Column(db.Integer(), db.ForeignKey('channel.id'), primary_key=True)
    state = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.String(255))

    def __str__(self):
        return "channel %d - %s: %s" % (self.channel_id, self.state, self.value)
