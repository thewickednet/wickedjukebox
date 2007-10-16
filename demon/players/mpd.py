"""
An interface to the music player daemon (mpd).
mpd is a client-server based audio player. It offers easy bindings to python
and hence it's a simple implementation
http://www.musicpd.org
"""

from demon.lib import mpdclient
from demon.model import getSetting
from datetime import datetime
import os, sys, time
from twisted.python import log

connection = None  # The interface to mpd
host       = None
port       = None
rootFolder = None
songStarted = None

def config(params):
   """
   Constructor
   Connects to the mpd-daemon.
   """
   global host, port, rootFolder

   # set up the connection to the daemon
   host       = params['host']
   port       = int(params['port'])
   rootFolder = params['rootFolder'].decode(sys.getfilesystemencoding())
   __connect()

def __disconnect():
   "Disconnect from mpd-player"
   global connection
   connection = None

def __connect():
   """
   Connect to the mpd-player.
   """
   global connection

   while True:
      try:
         log.msg( "Connecting to MPD backend..." )
         connection = mpdclient.MpdController( host, port )
      except mpdclient.MpdConnectionPortError, ex:
         log.err("Error connecting to the player.")
         time.sleep(1)
         continue
      break
   log.msg( "... MPD connected" )

def getPosition():
   """
   Returns the current position in the song. (currentSec, totalSec)
   """
   out = (0,0)
   try:
      pos = connection.getSongPosition()
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

def getSong():
   """
   Returns the currently running song
   """
   while True:
      try:
         if connection.getCurrentSong() is False:
            return None

         return os.path.join(
               rootFolder,
               connection.getCurrentSong().path.decode(sys.getfilesystemencoding()))
      except mpdclient.MpdError, ex:
         if str(ex).find('not done processing current command') > 0:
            log.msg('"not done processing current command" received. Retrying')
            connection.clearError()
            time.sleep(1)
            continue
         elif str(ex).find('playlistLength not found') > 0:
            log.msg('"playlistLength not found" received. Reconnecting to backend...')
            __disconnect()
            time.sleep(1)
            __connect()
            continue
         elif str(ex).find('problem parsing song info') > 0:
            log.msg('"problem parsing song info" received. Retrying')
            connection.clearError()
            time.sleep(1)
            continue
         else:
            raise
      break

   return None

def playlistPosition():
   """
   Returns the position in the playlist as integer
   """
   return connection.status().song

def queue(filename):
   """
   Appends a new song to the playlist, and removes the first entry in the
   playlist if it's becoming too large. This prevents having huge playlists
   after a while playing.

   @type  filename: str
   @param filename: The full path of the file
   """
   global songStarted
   # with MPD, filenames are relative to the path specified in the mpd
   # config!! This is handled here.
   if filename[0:len(rootFolder)] == rootFolder:
      filename = filename[len(rootFolder)+1:]
   log.msg("queuing %s" % filename)
   try:
      connection.add([filename])
      if getSetting('sys_utctime', 0) == 0:
         songStarted = datetime.utcnow()
      else:
         songStarted = datetime.now()
      return True
   except Exception, ex:
      log.err( "error queuing (%s)." % ex )
      return False

   # keep the playlist clean
   try:
      if connection.getStatus().playlistLength > 2:
         connection.delete([0])
   except mpdclient.MpdError, ex:
      log.err()

def playlistSize():
   """
   Returns the complete size of the playlist
   """
   return connection.getStatus().playlistLength

def cropPlaylist(length=2):
   """
   Removes items from the *beginning* of the playlist to ensure it has only
   a fixed number of entries.

   @type  length: int
   @param length: The new size of the playlist
   """
   try:
      if connection.getStatus().playlistLength > length:
         connection.delete(range(0,
            connection.getStatus().playlistLength - length))
   except mpdclient.MpdError, ex:
      print str(ex)

def clearPlaylist():
   """
   Clears the player's playlist
   """
   cropPlaylist(0)

def skipSong():
   """
   Skips the current song
   """
   connection.next()

def stopPlayback():
   """
   Stops playback
   """
   connection.stop()

def pausePlayback():
   """
   Pauses playback
   """
   connection.pause()

def startPlayback():
   """
   Starts playback
   """
   connection.play()

def status():
   """
   Returns the status of the player (play, stop, pause)
   """
   while True:
      try:
         if connection.getStatus().state == 1:
            return 'stop'
         elif connection.getStatus().state == 2:
            return 'play'
         elif connection.getStatus().state == 3:
            return 'pause'
         else:
            return 'unknown (%s)' % connection.getStatus().state
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

def updatePlaylist():
   connection.sendUpdateCommand()

