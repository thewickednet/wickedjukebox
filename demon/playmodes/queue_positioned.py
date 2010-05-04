#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Strict FIFO Queuing (ordered by position)
Pops off the song with position 1, then substracts 1 from the position field of
each item and finally removes all items with an id smaller than -10
"""

from demon.dbmodel import Session, QueueItem, queueTable, songTable, \
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

   session = Session()

   # determine the next position
   old = session.query(QueueItem)
   old = old.filter( queueTable.c.position > 0 )
   old = old.order_by=('-position')
   old = old.first()
   if old:
      nextPos = old.position + 1
   else:
      nextPos = 1

   qi = QueueItem()
   qi.position = nextPos
   qi.added    = datetime.now()
   qi.song_id  = songID
   qi.user_id  = userID
   qi.channel_id = channelID

   session.add(qi)
   session.close()

def list( channelID ):
   """
   Returns an ordered list of the items on the queue including position.
   """
   q = queueTable.join(songTable) \
       .join(artistTable)         \
       .join(albumTable, onclause=songTable.c.album_id==albumTable.c.id) \
       .select(order_by=queueTable.c.position, use_labels=True) \
       .where( queueTable.c.channel_id == channelID )
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

def dequeue( channelID ):
   """
   Return the filename of the next item on the queue. If the queue is empty,
   return None

   @type  channelID: int
   @param channelID: The id of the channel
   """

   session = Session()

   nextSong = session.query(QueueItem) \
         .filter(queueTable.c.position == 1 ) \
         .filter(queueTable.c.channel_id == channelID ) \
         .first()

   if nextSong:
      song = nextSong.song
   else:
      song = None

   if song:

      queueTable.update().where(queueTable.c.channel_id == channelID).values( {queueTable.c.position:queueTable.c.position-1} ).execute()
      queueTable.delete( queueTable.c.position < -20 )

      session.close()
      return song

   session.close()
   return None

def moveup( channelID, qid, delta):
   """
   Move a song upwards in the queue by <delta> steps
   (meaning it will be played earlier).

   @type channelID: int
   @param channelID: The channel ID

   @type  delta: int
   @param delta: How many steps the song is move up in the queue

   @type  qid: int
   @param qid: The database ID of the queue item (*not* the song!)
   """

   session = Session()

   qitem = session.query(QueueItem).get(qid)

   # we only need to do this for songs that are not already queue as next song
   if qitem.position > 1 and (qitem.position - delta) > 1:
      old_position = qitem.position
      min = old_position - delta
      max = old_position
      queueTable.update( and_( queueTable.c.position <= max,
                               queueTable.c.position >= min,
                               queueTable.c.channel_id == channelID
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
                               queueTable.c.position < qitem.position,
                               queueTable.c.channel_id == channelID
                             ),
                         values = {
                            queueTable.c.position:queueTable.c.position+1
                         } ).execute()
      queueTable.update( queueTable.c.id == qitem.id,
                         values = {
                            queueTable.c.position:1
                         } ).execute()
   session.close()

def movedown( channelID, qid, delta):
   """
   Move a song downwards in the queue by <delta> steps
   (meaning it will be played later).

   @type channelID: int
   @param channelID: The channel ID

   @type  delta: int
   @param delta: How many steps the song is move down in the queue

   @type  qid: int
   @param qid: The database ID of the queue item (*not* the song!)
   """

   session = Session()

   qitem = session.query(QueueItem).get(qid)

   qitem_bot = session.query(QueueItem).select(order_by=['-position'])
   if qitem_bot != []:
      bottom = qitem_bot[0].position
   else:
      bottom = 1

   # we only need to do this for songs that are not already at the end of the queue
   if qitem.position < bottom and (qitem.position + delta) < bottom:
      old_position = qitem.position
      min = old_position
      max = old_position + delta
      queueTable.update( and_( queueTable.c.position <= max,
                               queueTable.c.position >= min,
                               queueTable.c.channel_id == channelID
                             ),
                         values = {
                            queueTable.c.position:queueTable.c.position-1
                         } ).execute()
      queueTable.update( queueTable.c.id == qitem.id,
                         values = {
                            queueTable.c.position: max
                         } ).execute()
   elif qitem.position < bottom and (qitem.position + delta) > bottom:
      queueTable.update( and_( queueTable.c.position <= bottom,
                               queueTable.c.position > qitem.position,
                               queueTable.c.channel_id == channelID
                             ),
                         values = {
                            queueTable.c.position:queueTable.c.position-1
                         } ).execute()
      queueTable.update( queueTable.c.id == qitem.id,
                         values = {
                            queueTable.c.position: bottom
                         } ).execute()
   session.close()

def movetop( channelID, qid ):
   """
   Move a song to the top of the queue (meaning it will be played next)

   @type channelID: int
   @param channelID: The channel ID

   @type  qid: int
   @param qid: The database ID of the queue item (*not* the song!)
   """
   pass

def movebottom( channelID, qid ):
   """
   Move a song to the bottom of the queue (meaning it will be played last)

   @type channelID: int
   @param channelID: The channel ID

   @type  qid: int
   @param qid: The database ID of the queue item (*not* the song!)
   """
   pass
