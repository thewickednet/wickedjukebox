# -*- coding: utf-8 -*-

from flask import Blueprint

from ..services import artist, album
from . import route

bp = Blueprint('artist', __name__, url_prefix='/artist')


@route(bp, '/')
def list():
    """Returns a list of artist instances."""
    return artist.all()


@route(bp, '/<artist_id>')
def show(artist_id):
    """Returns an artist instance."""
    return artist.get_or_404(artist_id)


@route(bp, '/<artist_id>/albums')
def songs(artist_id):
    print("show_artist_albums")
    """Returns the songs of an album ."""
    return album.find(artist_id=artist_id).order_by('release_date DESC, name').all()
