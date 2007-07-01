#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Strict FIFO Queuing. No voting and such.
First song queued is also the first song popped off the queue
"""

from demon.model import create_session, QueueItem

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

   return nextSong


