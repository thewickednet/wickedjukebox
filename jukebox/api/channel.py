# -*- coding: utf-8 -*-

from flask import Blueprint

from ..services import channel
from . import route

bp = Blueprint('channel', __name__, url_prefix='/channel')


@route(bp, '/<channel_id>')
def show(channel_id):
    """Returns a channel instance."""
    return channel.get_or_404(channel_id)
