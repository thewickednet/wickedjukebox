import mpdclient
import os, sys, time, traceback
import threading
from twisted.python import log

try:
   import shoutpy
   shoutpy_available = True
except:
   shoutpy_available = False

def createPlayer(playerName, backend_params):

   # parse parameters, and put them into a dictionary
   params = {}
   if backend_params is not None:
      for param in backend_params.split(','):
         key, value = param.split('=')
         params[key.strip()] = value.strip()

   # create the specified player
   if playerName == 'mpd':
      return MPD(params)
   elif playerName == 'icecast':
      return Icecast(params)

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
      self.__rootFolder = params['rootFolder'].decode(sys.getfilesystemencoding())
      self.__connect()

   def __disconnect(self):
      "Disconnect from mpd-player"
      self.__connection = None

   def __connect(self):
      """
      Connect to the mpd-player.
      """

      while True:
         try:
            log.msg( "Connecting to MPD backend..." )
            self.__connection = mpdclient.MpdController(
                  self.__host,
                  self.__port)
         except mpdclient.MpdConnectionPortError, ex:
            log.err("Error connecting to the player.")
            time.sleep(1)
            continue
         break
      log.msg( "... MPD connected" )

   def getPosition(self):
      """
      Returns the current position in the song. (currentSec, totalSec)
      """
      out = (0,0)
      try:
         pos = self.__connection.getSongPosition()
         if pos:
            out = (pos[0], pos[1])
         else:
            out = (0,0)
      except mpdclient.MpdError, ex:
         if str(ex).find('not done processing current command') > 0:
            pass
         else:
            raise

      return out

   def getSong(self):
      """
      Returns the currently running song
      """
      while True:
         try:
            if self.__connection.getCurrentSong() is False:
               return None

            return os.path.join(
                  self.__rootFolder,
                  self.__connection.getCurrentSong().path.decode(sys.getfilesystemencoding()))
         except mpdclient.MpdError, ex:
            if str(ex).find('not done processing current command') > 0:
               log.msg('"not done processing current command" received. Retrying')
               self.__connection.clearError()
               time.sleep(1)
               continue
            elif str(ex).find('playlistLength not found') > 0:
               log.msg('"playlistLength not found" received. Reconnecting to backend...')
               self.__disconnect()
               time.sleep(1)
               self.__connect()
               continue
            elif str(ex).find('problem parsing song info') > 0:
               log.msg('"problem parsing song info" received. Retrying')
               self.__connection.clearError()
               time.sleep(1)
               continue
            else:
               raise
         break

      return None

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
      if filename[0:len(self.__rootFolder)] == self.__rootFolder:
         filename = filename[len(self.__rootFolder)+1:]
      log.msg("queuing %s" % filename)
      try:
         self.__connection.add([filename])
         return True
      except Exception, ex:
         log.err( "error queuing (%s)." % ex )
         return False

      # keep the playlist clean
      try:
         if self.__connection.getStatus().playlistLength > 2:
            self.__connection.delete([0])
      except mpdclient.MpdError, ex:
         log.err()

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
         length - The new size of the playlist (optional, default=2)
      """
      try:
         if self.__connection.getStatus().playlistLength > length:
            self.__connection.delete(range(0,
               self.__connection.getStatus().playlistLength - length))
      except mpdclient.MpdError, ex:
         print str(ex)

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
      while True:
         try:
            if self.__connection.getStatus().state == 1:
               return 'stop'
            elif self.__connection.getStatus().state == 2:
               return 'play'
            elif self.__connection.getStatus().state == 3:
               return 'pause'
            else:
               return 'unknown (%s)' % self.__connection.getStatus().state
         except mpdclient.MpdError, ex:
            if str(ex).find('not done processing current command') > 0:
               log.msg("'Not done proc. command' error skipped")
               time.sleep(1)
               continue
            elif str(ex).find("playlistLength not found") > 0:
               log.msg("'playlistLength not found' error skipped")
               time.sleep(1)
               continue
            else:
               try:
                  raise
               except mpdclient.MpdStoredError:
                  return 'stop'
         break;

      return 'unknown'

   def updatePlaylist(self):
      self.__connection.sendUpdateCommand()

class Icecast:

   def __init__(self, params):
      log.msg( "connection to icecast server (params = %s)" % params )
      self.__port     = int(params['port'])
      self.__mount    = str(params['mount'])
      self.__password = str(params['pwd'])
      self.__player   = Shoutcast_Player(self.__password,
                                         self.__mount,
                                         self.__port)

   def cropPlaylist(self, length=2):
      """
      Removes items from the *beginning* of the playlist to ensure it has only
      a fixed number of entries.

      PARAMETERS
         length - The new size of the playlist (optional, default=2)
      """
      log.msg( "[Icecast] cropping pl to %d songs" % length )
      self.__player.cropPlaylist(length)

   def getPosition(self):
      # now, the position is a challenge. If we have a CBR file, all is fine
      # and we can easily determine the duration. With VBR's that's very
      # difficult however. We use a simple cheat to overcome this. We simply
      # monitor the file position. So when asked for the position we return (0,
      # 100) so we in fact fool the juggler by telling it we have played 0 out
      # of 100 seconds. Then if we played a certain percentage, we immediately
      # jump to (99, 100). It's ugly, but should work.
      if self.__player.position > 90.0:
         return (99, 100)
      else:
         return (0, 100)

   def getSong(self):
      return self.__player.currentSong()

   def queue(self, filename):
      log.msg( "[Icecast] received a queue (%s)" % filename[0:10] )
      return self.__player.queue(filename)

   def skipSong(self):
      log.msg( "[Icecast] received a skip request" )
      return self.__player.skip()

   def stopPlayback(self):
      self.__player.stop()

   def pausePlayback(self):
      pass

   def startPlayback(self):
      self.__player.start()

   def status(self):
      pass

class Shoutcast_Player(threading.Thread):

   def __init__(self, password='hackme', mount='/wicked.mp3', port=8000):
      self.__keepRunning      = True
      self.__progress         = (0,0) # (streamed_bytes, total_bytes)
      self.__queue            = []
      self.__currentSong      = ''
      self.__triggerSkip      = False

      if shoutpy_available:
         self.__server           = shoutpy.Shout()
         self.__server.format    = shoutpy.FORMAT_MP3
         self.__server.user      = "source"
         self.__server.password  = password
         self.__server.mount     = mount
         self.__server.port      = port
         self.__server.open()
      else:
         log.err( "ERROR: Trying to create a shoupy-instance, but shoutpy is not installed!" )
      threading.Thread.__init__(self)

   def run(self):

      while self.__keepRunning is True:

         if len(self.__queue) > 0:
            self.__currentSong = self.__queue.pop(0)

            f = open(self.__currentSong, "rb")

            buf = f.read(32)
            self.__progress = (0, os.stat(self.__currentSong).st_size)

            # stream the file as long as the player is running, or as long as
            # it's not skipped
            while not self.__triggerSkip and self.__keepRunning and buf:

               self.__server.send(buf)
               self.__progress = (self.__progress[0]+len(buf),
                                  self.__progress[1])
               buf = f.read(16)
               self.__server.sync()
            f.close()

            log.msg( "Shoutcast song finished" )

            # if we fell through the previous loop because a skip was
            # requested, we need to reset that value. Otherwise we keep
            # skipping
            if self.__triggerSkip:
               self.__triggerSkip = False


      self.__server.close()

   def skip(self):
      log.msg( "Shoutcast player got a skip request" )
      self.__triggerSkip = True

   def queue(self, filename):
      self.__queue.append(filename)

   def currentSong(self):
      return self.__currentSong

   def position(self):
      """
      Returns a percentage of how far we are in the song
      """
      return float(self.__progress[0]) / float(self.__progress[1]) * 100.0

   def pause(self):
      pass

   def skip(self):
      pass

   def stop(self):
      log.msg( "Shoutcast player got a stop request" )
      self.__keepRunning = False

   def play(self):
      pass

   def disconnect(self):
      self.__keepRunning = False

   def cropPlaylist(self, length):
      while len(self.__queue) > length:
         self.__queue = self.__queue[1:]
