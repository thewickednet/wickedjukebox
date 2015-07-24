# -*- coding: utf-8 -*-

from flask import Blueprint

from ..services import album, song
from . import route

bp = Blueprint('album', __name__, url_prefix='/album')


@route(bp, '/<album_id>')
def show(album_id):
    print("show_albums")
    """Returns an album instance."""
    return album.get_or_404(album_id)


@route(bp, '/<album_id>/songs')
def songs(album_id):
    print("show_album_songs")
    """Returns the songs of an album ."""
    return song.find(album_id=album_id).order_by('track_no').all()
