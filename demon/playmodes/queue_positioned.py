#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Strict FIFO Queuing (ordered by position)
Pops off the song with position 1, then substracts 1 from the position field of
each item and finally removes all items with an id smaller than -10
"""

from demon.model import create_session, QueueItem, queueTable, songTable, \
                        artistTable, albumTable
from datetime import datetime
from sqlalchemy import and_

def enqueue(songID, userID, channelID):
   """
   Enqueues a song onto a queue of a given channel

   @type  songID: int
   @param songID: The id of the song to be enqueued

   @type  channelID: int
   @param channelID: The id of the channel

   @type  userID: int
   @param userID: The user who added the queue action
   """

   sess = create_session()

   # determine the next position
   old = sess.query(QueueItem).select( QueueItem.c.position > 0, order_by=['-position'] )
   if old != []:
      nextPos = old[0].position + 1
   else:
      nextPos = 1

   qi = QueueItem()
   qi.position = nextPos
   qi.added    = datetime.now()
   qi.song_id  = songID
   qi.user_id  = userID
   qi.channel_id = channelID

   sess.save(qi)
   sess.flush()
   sess.close()

def list():
   """
   Returns an ordered list of the items on the queue including position.
   """
   from sqlalchemy import eagerload
   q = queueTable.join(songTable) \
       .join(artistTable)         \
       .join(albumTable, onclause=songTable.c.album_id==albumTable.c.id) \
       .select(order_by=queueTable.c.position, use_labels=True)
   items = q.execute()
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
      out.append( data )
   return out

def dequeue():
   """
   Return the filename of the next item on the queue. If the queue is empty,
   return None
   """

   sess = create_session()
   nextSong = sess.query(QueueItem).selectfirst_by(QueueItem.c.position == 1 )

   if nextSong is not None:
      song = nextSong.song
   else:
      song = None

   sess.close()

   if song is not None:

      queueTable.update( values = {queueTable.c.position:queueTable.c.position-1} ).execute()
      queueTable.delete( queueTable.c.position < -20 )

      return song

   return None

def moveup(qid, delta):
   """
   Move a song upwards in the queue by <delta> steps
   (meaning it will be played earlier).

   @type  delta: int
   @param delta: How many steps the song is move up in the queue

   @type  qid: int
   @param qid: The database ID of the queue item (*not* the song!)
   """
   sess = create_session()
   qitem = sess.query(QueueItem).get(qid)
   sess.close()

   # we only need to do this for songs that are not already queue as next song
   if qitem.position > 1 and (qitem.position - delta) > 1:
      old_position = qitem.position
      min = old_position - delta
      max = old_position
      queueTable.update( and_( queueTable.c.position <= max,
                               queueTable.c.position >= min
                             ),
                         values = {
                            queueTable.c.position:queueTable.c.position+1
                         } ).execute()
      queueTable.update( queueTable.c.id == qitem.id,
                         values = {
                            queueTable.c.position:min
                         } ).execute()
   elif qitem.position > 1 and (qitem.position - delta) < 1:
      queueTable.update( and_( queueTable.c.position >= 1,
                               queueTable.c.position < qitem.position
                             ),
                         values = {
                            queueTable.c.position:queueTable.c.position+1
                         } ).execute()
      queueTable.update( queueTable.c.id == qitem.id,
                         values = {
                            queueTable.c.position:1
                         } ).execute()


def movedown(qid, delta):
   """
   Move a song downwards in the queue by <delta> steps
   (meaning it will be played later).

   @type  delta: int
   @param delta: How many steps the song is move down in the queue

   @type  qid: int
   @param qid: The database ID of the queue item (*not* the song!)
   """
   sess = create_session()
   qitem = sess.query(QueueItem).get(qid)

   qitem_bot = sess.query(QueueItem).select(order_by=['-position'])
   if qitem_bot != []:
      bottom = qitem_bot[0].position
   else:
      bottom = 1

   sess.close()

   # we only need to do this for songs that are not already at the end of the queue
   if qitem.position < bottom and (qitem.position + delta) < bottom:
      old_position = qitem.position
      min = old_position
      max = old_position + delta
      queueTable.update( and_( queueTable.c.position <= max,
                               queueTable.c.position >= min
                             ),
                         values = {
                            queueTable.c.position:queueTable.c.position-1
                         } ).execute()
      queueTable.update( queueTable.c.id == qitem.id,
                         values = {
                            queueTable.c.position:max
                         } ).execute()
   elif qitem.position < bottom and (qitem.position + delta) > bottom:
      queueTable.update( and_( queueTable.c.position <= bottom,
                               queueTable.c.position > qitem.position
                             ),
                         values = {
                            queueTable.c.position:queueTable.c.position-1
                         } ).execute()
      queueTable.update( queueTable.c.id == qitem.id,
                         values = {
                            queueTable.c.position:bottom
                         } ).execute()

def movetop(qid):
   """
   Move a song to the top of the queue (meaning it will be played next)

   @type  qid: int
   @param qid: The database ID of the queue item (*not* the song!)
   """
   pass

def movebottom(qid):
   """
   Move a song to the bottom of the queue (meaning it will be played last)

   @type  qid: int
   @param qid: The database ID of the queue item (*not* the song!)
   """
   pass
