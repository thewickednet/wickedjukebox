#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Strict FIFO Queuing (ordered by position)
Pops off the song with position 1, then substracts 1 from the position field of
each item and finally removes all items with an id smaller than -10
"""

from demon.model import create_session, QueueItem, queueTable

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

