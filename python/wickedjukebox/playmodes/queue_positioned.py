#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Strict FIFO Queuing (ordered by position)
Pops off the song with position 1, then substracts 1 from the position field of
each item and finally removes all items with an id smaller than -10
"""

from wickedjukebox.model.core import (
        SESSION,
        QueueItem,
        QUEUE_TABLE,
        SONG_TABLE,
        ARTIST_TABLE,
        ALBUM_TABLE)
from datetime import datetime
from sqlalchemy import and_

def enqueue(song_id, user_id, channel_id):
    """
    Enqueues a song onto a queue of a given channel

    @type  song_id: int
    @param song_id: The id of the song to be enqueued

    @type  channel_id: int
    @param channel_id: The id of the channel

    @type  user_id: int
    @param user_id: The user who added the queue action
    """

    session = SESSION()

    # determine the next position
    old = session.query(QueueItem)
    old = old.filter( QUEUE_TABLE.c.position > 0 )
    old = old.order_by = ('-position')
    old = old.first() # pylint: disable=E1101
    if old:
        next_pos = old.position + 1
    else:
        next_pos = 1

    queue_item = QueueItem()
    queue_item.position = next_pos
    queue_item.added = datetime.now()
    queue_item.song_id = song_id
    queue_item.user_id = user_id
    queue_item.channel_id = channel_id

    session.add(queue_item)
    session.close()

def list(channel_id):
    """
    Returns an ordered list of the items on the queue including position.
    """
    query = QUEUE_TABLE.join(SONG_TABLE) \
         .join(ARTIST_TABLE) \
         .join(ALBUM_TABLE, onclause=SONG_TABLE.c.album_id==ALBUM_TABLE.c.id) \
         .select(order_by=QUEUE_TABLE.c.position, use_labels=True) \
         .where( QUEUE_TABLE.c.channel_id == channel_id )
    items = query.execute()
    out = []
    for item in items:
        data = {
            'position': item[QUEUE_TABLE.c.position],
            'song': {
                'id': item[SONG_TABLE.c.id],
                'title': item[SONG_TABLE.c.title].encode('utf-8'),
                'duration': item[SONG_TABLE.c.duration],
            },
            'album': {
                'id': item[ALBUM_TABLE.c.id],
                'name': item[ALBUM_TABLE.c.name].encode('utf-8')
            },
            'artist': {
                'id': item[ARTIST_TABLE.c.id],
                'name': item[ARTIST_TABLE.c.name].encode('utf-8')
            }
        }
        out.append( data )
    return out

def dequeue( channel_id ):
    """
    Return the filename of the next item on the queue. If the queue is empty,
    return None

    @type  channel_id: int
    @param channel_id: The id of the channel
    """

    session = SESSION()

    next_song = session.query(QueueItem) \
            .filter(QUEUE_TABLE.c.position == 1 ) \
            .filter(QUEUE_TABLE.c.channel_id == channel_id ) \
            .first()

    if next_song:
        song = next_song.song
    else:
        song = None

    if song:

        QUEUE_TABLE.update().where(
                QUEUE_TABLE.c.channel_id == channel_id).values(
                        {QUEUE_TABLE.c.position:QUEUE_TABLE.c.position-1}
                        ).execute()
        QUEUE_TABLE.delete(QUEUE_TABLE.c.position < -20)

        session.close()
        return song

    session.close()
    return None

def moveup( channel_id, qid, delta):
    """
    Move a song upwards in the queue by <delta> steps
    (meaning it will be played earlier).

    @type channel_id: int
    @param channel_id: The channel ID

    @type  delta: int
    @param delta: How many steps the song is move up in the queue

    @type  qid: int
    @param qid: The database ID of the queue item (*not* the song!)
    """

    session = SESSION()

    qitem = session.query(QueueItem).get(qid)

    # we only need to do this for songs that are not already queue as next song
    if qitem.position > 1 and (qitem.position - delta) > 1:
        old_position = qitem.position
        min_ = old_position - delta
        max_ = old_position
        QUEUE_TABLE.update(
            and_(QUEUE_TABLE.c.position <= max_,
                QUEUE_TABLE.c.position >= min_,
                QUEUE_TABLE.c.channel_id == channel_id),
            values = {
                QUEUE_TABLE.c.position:QUEUE_TABLE.c.position + 1
            } ).execute()
        QUEUE_TABLE.update(
            QUEUE_TABLE.c.id == qitem.id,
            values = {
                QUEUE_TABLE.c.position: min_
            }).execute()

    elif qitem.position > 1 and (qitem.position - delta) < 1:
        QUEUE_TABLE.update(
            and_(QUEUE_TABLE.c.position >= 1,
                QUEUE_TABLE.c.position < qitem.position,
                QUEUE_TABLE.c.channel_id == channel_id
            ),
            values = {
                QUEUE_TABLE.c.position:QUEUE_TABLE.c.position + 1
            }).execute()
        QUEUE_TABLE.update(
            QUEUE_TABLE.c.id == qitem.id,
            values = {
                QUEUE_TABLE.c.position: 1
            }).execute()

    session.close()

def movedown( channel_id, qid, delta):
    """
    Move a song downwards in the queue by <delta> steps
    (meaning it will be played later).

    @type channel_id: int
    @param channel_id: The channel ID

    @type  delta: int
    @param delta: How many steps the song is move down in the queue

    @type  qid: int
    @param qid: The database ID of the queue item (*not* the song!)
    """

    session = SESSION()

    qitem = session.query(QueueItem).get(qid)

    qitem_bot = session.query(QueueItem).select(order_by=['-position'])
    if qitem_bot:
        bottom = qitem_bot[0].position
    else:
        bottom = 1

    # we only need to do this for songs that are not already at the end of the
    # queue
    if qitem.position < bottom and (qitem.position + delta) < bottom:
        old_position = qitem.position
        min_ = old_position
        max_ = old_position + delta
        QUEUE_TABLE.update(
            and_(QUEUE_TABLE.c.position <= max_,
                QUEUE_TABLE.c.position >= min_,
                QUEUE_TABLE.c.channel_id == channel_id
            ),
            values = {
                QUEUE_TABLE.c.position:QUEUE_TABLE.c.position - 1
            }).execute()

        QUEUE_TABLE.update(
            QUEUE_TABLE.c.id == qitem.id,
            values = {
                QUEUE_TABLE.c.position: max_
            }).execute()

    elif qitem.position < bottom and (qitem.position + delta) > bottom:
        QUEUE_TABLE.update(
            and_(QUEUE_TABLE.c.position <= bottom,
                QUEUE_TABLE.c.position > qitem.position,
                QUEUE_TABLE.c.channel_id == channel_id
            ),
            values = {
                QUEUE_TABLE.c.position:QUEUE_TABLE.c.position - 1
            }).execute()

        QUEUE_TABLE.update(
            QUEUE_TABLE.c.id == qitem.id,
            values = {
                QUEUE_TABLE.c.position: bottom
            }).execute()

    session.close()

def movetop( channel_id, qid ):
    """
    Move a song to the top of the queue (meaning it will be played next)

    @type channel_id: int
    @param channel_id: The channel ID

    @type  qid: int
    @param qid: The database ID of the queue item (*not* the song!)
    """
    # pylint: disable=W0613
    pass

def movebottom( channel_id, qid ):
    """
    Move a song to the bottom of the queue (meaning it will be played last)

    @type channel_id: int
    @param channel_id: The channel ID

    @type  qid: int
    @param qid: The database ID of the queue item (*not* the song!)
    """
    # pylint: disable=W0613
    pass
