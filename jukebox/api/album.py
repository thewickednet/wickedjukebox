# -*- coding: utf-8 -*-

from flask import Blueprint

from ..services import album
from . import route

bp = Blueprint('album', __name__, url_prefix='/album')


@route(bp, '/<album_id>')
def show(album_id):
    """Returns an album instance."""
    return album.get_or_404(album_id)
