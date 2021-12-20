#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Strict FIFO Queuing (ordered by position)
Pops off the song with position 1, then substracts 1 from the position field of
each item and finally removes all items with an id smaller than -10
"""
from datetime import datetime

from sqlalchemy import and_
from wickedjukebox.demon.dbmodel import (QueueItem, albumTable,
                                         artistTable, queueTable, songTable)


def enqueue(session, songID, userID, channel_id):
    """
    Enqueues a song onto a queue of a given channel

    @type  session: Session
    @param session: The DB Session

    @type  songID: int
    @param songID: The id of the song to be enqueued

    @type  channel_id: int
    @param channel_id: The id of the channel

    @type  userID: int
    @param userID: The user who added the queue action
    """

    # determine the next position
    old = session.query(QueueItem)
    old = old.filter(queueTable.c.position > 0)
    old = old.order_by(QueueItem.position.desc())
    old = old.first()
    if old:
        nextPos = old.position + 1
    else:
        nextPos = 1

    queue_item = QueueItem()
    queue_item.position = nextPos
    queue_item.added = datetime.now()
    queue_item.song_id = songID
    queue_item.user_id = userID
    queue_item.channel_id = channel_id

    session.add(queue_item)
    session.flush()


def list(session, channel_id):
    """
    Returns an ordered list of the items on the queue including position.
    """
    query = queueTable.join(songTable) \
        .join(artistTable) \
        .join(albumTable, onclause=songTable.c.album_id == albumTable.c.id) \
        .select(order_by=queueTable.c.position, use_labels=True) \
        .where(queueTable.c.channel_id == channel_id)

    items = session.execute(query)
    out = []
    for item in items:
        data = {
            'position': item[queueTable.c.position],
            'song': {
                'id':       item[songTable.c.id],
                'title':    item[songTable.c.title].encode('utf-8'),
                'duration': item[songTable.c.duration],
            },
            'album': {
                'id':   item[albumTable.c.id],
                'name': item[albumTable.c.name].encode('utf-8')
            },
            'artist': {
                'id':   item[artistTable.c.id],
                'name': item[artistTable.c.name].encode('utf-8')
            }
        }
        out.append(data)
    return out


def dequeue(session, channel_id):
    """
    Return the filename of the next item on the queue. If the queue is empty,
    return None

    @type  session: Session
    @param session: The DB Session

    @type  channel_id: int
    @param channel_id: The id of the channel
    """

    nextSong = session.query(QueueItem) \
        .filter(queueTable.c.position == 1) \
        .filter(queueTable.c.channel_id == channel_id) \
        .first()

    if nextSong:
        song = nextSong.song
    else:
        song = None

    if song:
        query = queueTable.update().where(queueTable.c.channel_id == channel_id).values(
            {queueTable.c.position: queueTable.c.position-1})
        session.execute(query)
        session.execute(queueTable.delete(queueTable.c.position < -20))

        session.flush()
        session.expire_all()
        return song

    session.flush()
    return None


def moveup(session, channel_id, qid, delta):
    """
    Move a song upwards in the queue by <delta> steps
    (meaning it will be played earlier).

    @type  session: Session
    @param session: The DB Session

    @type channel_id: int
    @param channel_id: The channel ID

    @type  delta: int
    @param delta: How many steps the song is move up in the queue

    @type  qid: int
    @param qid: The database ID of the queue item (*not* the song!)
    """

    qitem = session.query(QueueItem).get(qid)
    if qitem is None:
        return

    # we only need to do this for songs that are not already queued as next song
    if qitem.position > 1 and (qitem.position - delta) > 1:
        old_position = qitem.position
        min = old_position - delta
        max = old_position
        query = queueTable.update(and_(
            queueTable.c.position <= max,
            queueTable.c.position >= min,
            queueTable.c.channel_id == channel_id
        ), values={
            queueTable.c.position: queueTable.c.position+1
        })
        session.execute(query)
        query = queueTable.update(queueTable.c.id == qitem.id,
                          values={
                              queueTable.c.position: min
                          })
        session.execute(query)
    elif qitem.position > 1 and (qitem.position - delta) < 1:
        query = queueTable.update(and_(
            queueTable.c.position >= 1,
            queueTable.c.position < qitem.position,
            queueTable.c.channel_id == channel_id
        ), values={
            queueTable.c.position: queueTable.c.position+1
        })
        session.execute(query)
        query = queueTable.update(queueTable.c.id == qitem.id,
                          values={
                              queueTable.c.position: 1
                          })
        session.execute(query)
    session.flush()
    session.expire_all()


def movedown(session, channel_id, qid, delta):
    """
    Move a song downwards in the queue by <delta> steps
    (meaning it will be played later).

    @type  session: Session
    @param session: The DB Session

    @type channel_id: int
    @param channel_id: The channel ID

    @type  delta: int
    @param delta: How many steps the song is move down in the queue

    @type  qid: int
    @param qid: The database ID of the queue item (*not* the song!)
    """

    qitem = session.query(QueueItem).get(qid)
    if qitem is None:
        return

    qitem_bot = session.query(QueueItem).order_by(QueueItem.position.desc())
    if qitem_bot != []:
        bottom = qitem_bot[0].position
    else:
        bottom = 1

    # we only need to do this for songs that are not already at the end of the
    # queue
    if qitem.position < bottom and (qitem.position + delta) < bottom:
        old_position = qitem.position
        min = old_position
        max = old_position + delta
        query = queueTable.update(and_(
            queueTable.c.position <= max,
            queueTable.c.position >= min,
            queueTable.c.channel_id == channel_id
        ), values={
            queueTable.c.position: queueTable.c.position-1
        })
        session.execute(query)
        query = queueTable.update(queueTable.c.id == qitem.id,
                          values={
                              queueTable.c.position: max
                          })
        session.execute(query)
    elif qitem.position < bottom < (qitem.position + delta):
        query = queueTable.update(and_(
            queueTable.c.position <= bottom,
            queueTable.c.position > qitem.position,
            queueTable.c.channel_id == channel_id
        ), values={
            queueTable.c.position: queueTable.c.position-1
        })
        session.execute(query)
        query = queueTable.update(queueTable.c.id == qitem.id,
                          values={
                              queueTable.c.position: bottom
                          })
        session.execute(query)
    session.flush()
    session.expire_all()
