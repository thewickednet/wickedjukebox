#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Strict FIFO Queuing. No voting and such.
First song queued is also the first song popped off the queue
"""

from demon.model import create_session, QueueItem
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

   qi = QueueItem()
   qi.position = 0
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
   pick one from the prediction queue
   """

   sess = create_session()
   nextSong = sess.query(QueueItem).selectfirst(order_by=['added', 'position'])
   if nextSong is not None:
      sess.delete(nextSong)

      sess.flush()
      sess.close()

      return nextSong.song

   return None
