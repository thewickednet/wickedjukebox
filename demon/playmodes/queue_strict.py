#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Strict FIFO Queuing. No voting and such.
First song queued is also the first song popped off the queue

@TODO: remove sqlalchemy references!
"""

from sqlalchemy.sql import insert, select
from demon.dbmodel import queueTable, QueueItem, Session
from datetime import datetime
import logging
LOG=logging.getLogger(__name__)

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

   insert( queueTable ).values({
         "position"   : 0,
         "added"      : datetime.now(),
         "song_id"    : songID,
         "user_id"    : userID,
         "channel_id" : channelID,
      }).execute()

def dequeue():
   """
   Return the filename of the next item on the queue. If the queue is empty,
   pick one from the prediction queue
   """

   session = Session()
   nextSong = session.query(QueueItem).order_by('added', 'position').first()
   if nextSong:
      session.delete(nextSong)
      session.close()
      return nextSong.song

   session.close()
   return None
