"""
A no-op player interface. Use this as blueprint for new player interfaces.
"""

def config(params):
   """
   This method gets called right after loading the module. "params" is a
   dictionary created from the "backend_params" field in the channel-settings.
   """

   pass #no-op

def getPosition():
   """
   Returns the current position in the song. (currentSec, totalSec)
   """

   return (0, 0)

def getSong():
   """
   Returns the full path to the currently running song
   """

   return None

def playlistPosition():
   """
   Returns the position in the playlist as integer
   """
   return 0

def queue(filename):
   """
   Appends a new song to the playlist, and removes the first entry in the
   playlist if it's becoming too large. This prevents having huge playlists
   after a while playing.

   @type  filename: str
   @param filename: The full path of the file
   """

   success = True
   return success

def playlistSize():
   """
   Returns the complete size of the playlist
   """
   return 0

def cropPlaylist(length=2):
   """
   Removes items from the *beginning* of the playlist to ensure it has only
   a fixed number of entries.

   @type  length: int
   @param length: The new size of the playlist
   """

   pass #no-op

def clearPlaylist():
   """
   Clears the player's playlist
   """
   cropPlaylist(0)

def skipSong():
   """
   Skips the current song
   """

   pass #no-op

def stopPlayback():
   """
   Stops playback
   """

   pass #no-op

def pausePlayback():
   """
   Pauses playback
   """

   pass #no-op

def startPlayback():
   """
   Starts playback
   """

   pass #no-op

def status():
   """
   Returns the status of the player (play, stop, pause, unknown)
   """

   return 'unknown'

def current_listeners():
   """
   Returns a list of unique identifiers of current listeners
   """
   return []
