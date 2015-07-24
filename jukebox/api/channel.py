# -*- coding: utf-8 -*-

from flask import Blueprint

from ..services import channel, queue, state, song
from . import route

bp = Blueprint('channel', __name__, url_prefix='/channel')


@route(bp, '/<channel_id>')
def show(channel_id):
    """Returns a channel instance."""
    return channel.get_or_404(channel_id)


@route(bp, '/<channel_id>/queue')
def queue_items(channel_id):
    print("show_channel_queue")
    """Returns the items of the queue"""
    m = queue.__model__
    return m.query.filter(m.channel_id == channel_id, m.position >= 0).order_by('position ASC').all()


@route(bp, '/<channel_id>/state')
def queue_state(channel_id):
    print("show_channel_queue")
    """Returns the items of the queue"""
    state_current_song = state.find(channel_id=channel_id, state='current_song').first()
    current_song = song.get(state_current_song.value)
    return current_song
