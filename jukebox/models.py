# -*- coding: utf-8 -*-

from .core import db
from .helpers import JsonSerializer


class ArtistJsonSerializer(JsonSerializer):
    __json_hidden__ = []


class Artist(ArtistJsonSerializer, db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(128))
