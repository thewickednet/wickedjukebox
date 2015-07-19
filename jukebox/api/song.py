# -*- coding: utf-8 -*-

from flask import Blueprint

from ..services import song
from . import route

bp = Blueprint('song', __name__, url_prefix='/song')


@route(bp, '/<song_id>')
def show(song_id):
    """Returns an song instance."""
    return song.get_or_404(song_id)
