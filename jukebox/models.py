# -*- coding: utf-8 -*-

from .core import db
from .helpers import JsonSerializer


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
    albums = db.relationship('Album')


class SongJsonSerializer(JsonSerializer):
    __json_hidden__ = ['localpath', 'checksum']


class Song(SongJsonSerializer, db.Model):
    __tablename__ = 'song'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(128))
    duration = db.Column(db.Float())
    year = db.Column(db.Integer())
    bitrate = db.Column(db.Integer())
    localpath = db.Column(db.String(255))
    downloaded = db.Column(db.Integer())
    filesize = db.Column(db.Integer())
    checksum = db.Column(db.String(14))
    lyrics = db.Column(db.Text())
    added = db.Column(db.DateTime())


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


class User(db.Model):
    __tablename__ = 'user'

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


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(32))
    admin = db.Column(db.Integer())
    nocredits = db.Column(db.Integer())
    queue_skip = db.Column(db.Integer())
    queue_remove = db.Column(db.Integer())
    queue_add = db.Column(db.Integer())
