"""
This is a no-op playmode used as blueprint for new playmodes.
Simply complete the methods in this module and make them return the right type
and you should be fine.
"""

#
# These imports might prove useful:
#
## from wickedjukebox.demon.dbmodel import Session, Song, engine
## import logging
## LOG = logging.getLogger(__name__)

def bootstrap(channel_id):
   """
   This is always called as soon as the module is loaded.
   It is used to bootstrap the module.

   Note that this will be called on each iteration, so it should cope with
   that. If you want to process this method only one you should deal with that
   internally (by using a sentinel variable for example).

   @param channel_id: The channel ID
   """
   pass


def get(channel_id):
   """
   Returns a random song.
   @param channel_id: The channel ID for which we are returning results
   @note: This method should *always* return a valid Song instance. Only
          return "None" if something seriously went wrong.

   @rtype:  None | Song
   @return: Either "None" if no random song could be determined,
            or a "Song" instance (as imported from wickedjukebox.demon.model
            --> see above)
   """

   return None

def peek(channel_id):
   """
   Returns the song that will play immediately after the current song
   @param channel_id: The channel ID for which we are returning results
   @note: Returns "None" if the playmode does not support this feature
   @rtype:  None | Song
   @return: Either "None" if the upcoming song cannot be determined
            or a "Song" instance (as imported from wickedjukebox.demon.model
            --> see above)
   """
   return None

def prefetch(channel_id, async=True):
   """
   Trigger prefetching of a song. This may be used when a client requests that
   the song marked as "upcoming song" is unwanted.

   Playmodes that do not support a lookahead (see also "peek") will simply do
   nothing when this method is called.
   @param channel_id: The channel ID for which we are returning results
   @param async: Whether to run the internal prefetch call asynchronously or
                 not. This MUST be implemented for asynchronous prefetchers to
                 ensure thread safety
   """
   pass

def test(channel_id):
   """
   Used to run a test on the random mode.This should return a list o tuples
   containing a Song instance as first element, and a dictionary of stats as
   second element.
   @param channel_id: The channel ID for which we are returning results
   @return: List of 2-tuples (Song, stats)
   """
   pass
