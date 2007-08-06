"""
This is a no-op playmode used as blueprint for new playmodes.
Simply complete the methods in this module and make them return the right type
and you should be fine.
"""

#
# These imports might prove useful:
#
## from demon.model import create_session, Song
## from twisted.python import log
## from demon.model import create_session, QueueItem

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

   pass

def dequeue():
   """
   Return the next song from the queue

   @rtype:  Song
   @return: This should return a valid "Song" instance, which points to the next song
            on the queue.
            If nothing was on the queue, or no song could be determnined, then return
            "None", so the system can fall back to random mode.
   """

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
   pass

def movedown(qid, delta):
   """
   Move a song downwards in the queue by <delta> steps
   (meaning it will be played later).

   @type  delta: int
   @param delta: How many steps the song is move down in the queue

   @type  qid: int
   @param qid: The database ID of the queue item (*not* the song!)
   """
   pass

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
