import mpdclient
def createPlayer(playerName, backend_params):

   # parse parameters, and put them into a dictionary
   params = {}
   for param in backend_params.split(','):
      key, value = param.split('=')
      params[key.strip()] = value.strip()

   # create the specified player
   if playerName == 'mpd':
      return MPD(params)

class MPD:
   """
   An interface to the music player daemon (mpd).
   mpd is a client-server based audio player. It offers easy bindings to python
   and hence it's a simple implementation
   http://www.musicpd.org
   """

   __connection = None  # The interface to mpd

   def __init__(self, params):
      """
      Constructor
      Connects to the mpd-daemon.
      """
      # set up the connection to the daemon
      self.__host       = params['host']
      self.__port       = int(params['port'])
      self.__rootFolder = params['rootFolder']
      self.__connect()

   def __connect(self):
      """
      Connect to the mpd-player.
      """
      try:
         self.__connection = mpdclient.MpdController(self.__host, self.__port)
      except mpdclient.MpdConnectionPortError, ex:
         import traceback
         self.__logger.error("Error connecting to the player:\n%s"
                             % traceback.format_exc())

   def getPosition(self):
      """
      Returns the current position in the song. (currentSec, totalSec)
      """
      pos = self.__connection.getSongPosition()
      if pos:
         return (pos[0], pos[1])
      else:
         return (0,0)

   def getSong(self):
      """
      Returns the currently running song
      """
      import os
      if self.__connection.getCurrentSong() is False:
         return False

      return os.path.join(
            self.__rootFolder,
            self.__connection.getCurrentSong().path)

   def playlistPosition(self):
      """
      Returns the position in the playlist as integer
      """
      return self.__connection.status().song

   def queue(self, filename):
      """
      Appends a new song to the playlist, and removes the first entry in the
      playlist if it's becoming too large. This prevents having huge playlists
      after a while playing.

      PARAMETERS
         filename -  The full path of the file
      """
      # with MPD, filenames are relative to the path specified in the mpd
      # config!! This is handled here.
      if filename.startswith(self.__rootFolder):
         filename = filename[len(self.__rootFolder)+1:]
      ##logging.info("queuing %s" % filename)
      self.__connection.add([filename])

      # keep the playlist clean
      if self.__connection.getStatus().playlistLength > 10:
         self.__connection.delete([0])

   def playlistSize(self):
      """
      Returns the complete size of the playlist
      """
      return self.__connection.getStatus().playlistLength

   def cropPlaylist(self, length=2):
      """
      Removes items from the *beginning* of the playlist to ensure it has only
      a fixed number of entries.

      PARAMETERS
         length - The new size of the playlist (optional, default=10)
      """
      if self.__connection.getStatus().playlistLength > length:
         self.__connection.delete(range(0,
            self.__connection.getStatus().playlistLength - length))

   def clearPlaylist(self):
      """
      Clears the player's playlist
      """
      self.cropPlaylist(0)

   def skipSong(self):
      """
      Skips the current song
      """
      self.__connection.next()

   def stopPlayback(self):
      """
      Stops playback
      """
      self.__connection.stop()

   def pausePlayback(self):
      """
      Pauses playback
      """
      self.__connection.pause()

   def startPlayback(self):
      """
      Starts playback
      """
      self.__connection.play()

   def status(self):
      """
      Returns the status of the player (play, stop, pause)
      """
      try:
         if self.__connection.getStatus().state == 1:
            return 'stop'
         elif self.__connection.getStatus().state == 2:
            return 'play'
         elif self.__connection.getStatus().state == 3:
            return 'pause'
      except mpdclient.MpdError, ex:
         if str(ex).find('not done processing current command') > 0:
            pass
         else:
            raise

      return 'unknown (%s)' % self.__connection.getStatus().state

   def updatePlaylist(self):
      self.__connection.sendUpdateCommand()


