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

def get(channel_id):
   """
   Returns a random song.
   @param channel_id: The channel ID for which we are returning results
   @note: This method should *always* return a valid Song instance. Only
          return "None" if something seriously went wrong.

   @rtype:  None | Song
   @return: Either "None" if no random song could be determined,
            or a "Song" instance (as imported from demon.model --> see above)
   """

   return None
