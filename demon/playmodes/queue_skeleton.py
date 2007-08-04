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

