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
