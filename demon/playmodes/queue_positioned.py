#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Strict FIFO Queuing (ordered by position)
Pops off the song with position 1, then substracts 1 from the position field of
each item and finally removes all items with an id smaller than -10
"""

from demon.model import create_session, QueueItem, queueTable
from datetime import datetime

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

