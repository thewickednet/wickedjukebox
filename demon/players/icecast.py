import os
import threading
from twisted.python import log
from datetime import datetime
from demon.model import getSetting
import shoutpy

STATUS_STOPPED=1
STATUS_PLAYING=2
STATUS_PAUSED=3

class Shoutcast_Player(threading.Thread):

   def __init__(self, password='hackme', mount='/wicked.mp3', port=8000):
      self.__keepRunning      = True
      self.__progress         = (0,0) # (streamed_bytes, total_bytes)
      self.__queue            = []
      self.__currentSong      = ''
      self.__triggerSkip      = False
      self.__server           = shoutpy.Shout()
      self.__server.format    = shoutpy.FORMAT_MP3
      self.__server.user      = "source"
      self.__server.password  = password
      self.__server.mount     = mount
      self.__server.port      = port
      ##self.__server.nonblocking = True
      self.__server.open()
      self.__status           = STATUS_STOPPED
      threading.Thread.__init__(self)

   def get_description(self, filename):
      try:
         meta = mutagen.File( filename )
         artist = "unkown artist"
         if meta.has_key( 'TPE1' ):
            artist = meta.get( 'TPE1' ).text[0]
         elif meta.has_key( 'artist' ):
            artist = meta.get('artist')[0]

         title =  "unknown song"
         if meta.has_key( 'TIT2' ):
            title = meta.get( 'TIT2' ).text[0]
         elif meta.has_key( 'title' ):
            title = meta.get('title')[0]
         return "%s - %s" % (artist, title)
      except:
         log.err( "%s contained no valid metadata!" % filename )
         return "unknown song"

   def run(self):

      while self.__keepRunning is True:

         if len(self.__queue) > 0:
            self.__currentSong = self.__queue.pop(0)

            f = open(self.__currentSong, "rb")
	    self.__server.metadata = {'song': self.get_description(self.__currentSong)}

            buf = f.read(4096)
            self.__progress = (0, os.stat(self.__currentSong).st_size)
            self.__status = STATUS_PLAYING

            # stream the file as long as the player is running, or as long as
            # it's not skipped
            while not self.__triggerSkip and self.__keepRunning and buf:

               try:
                  self.__server.send(buf)
                  self.__server.sync()
               except RuntimeError, ex:
                  if (str(ex).find("Socket error") > -1):
                     log.msg(str(ex))
                     self.__triggerSkip = True
                  else:
                     raise

               self.__progress = (self.__progress[0]+len(buf),
                                  self.__progress[1])
               buf = f.read(4096)
            f.close()

            log.msg( "Shoutcast song finished" )
            self.__status = STATUS_STOPPED

            # if we fell through the previous loop because a skip was
            # requested, we need to reset that value. Otherwise we keep
            # skipping
            if self.__triggerSkip:
               self.__triggerSkip = False

      log.msg("Shoutcast loop finished")

      self.__server.close()
      self.__status = STATUS_STOPPED

   def skip(self):
      log.msg( "Shoutcast player got a skip request" )
      self.__triggerSkip = True

   def queue(self, filename):
      if filename.endswith("mp3"):
         self.__queue.append(filename)
         return True
      else:
         return False

   def currentSong(self):
      return self.__currentSong

   def position(self):
      """
      Returns a percentage of how far we are in the song
      """
      # TODO: do some real calculations with bitrate (CBR & VBR) to return the
      #       position in seconds!
      try:
         return float(self.__progress[0]) / float(self.__progress[1]) * 100.0
      except ZeroDivisionError:
         return 0

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

   def status(self):
      if self.__status == STATUS_PAUSED:
         return 'pause'
      elif self.__status == STATUS_PLAYING:
         return 'play'
      elif self.__status == STATUS_STOPPED:
         return 'stop'
      else:
         return 'unknown'

# ----------------------------------------------------------------------------

__port     = None
__mount    = None
__password = None
__player   = None
songStarted = None

def config(params):
   global __port, __mount, __password, __player
   log.msg( "connection to icecast server (params = %s)" % params )
   __port     = int(params['port'])
   __mount    = str(params['mount'])
   __password = str(params['pwd'])
   __player   = Shoutcast_Player(__password,
                                 __mount,
                                 __port)

def cropPlaylist(length=2):
   """
   Removes items from the *beginning* of the playlist to ensure it has only
   a fixed number of entries.

   @type  length: int
   @param length: The new size of the playlist
   """
   log.msg( "[Icecast] cropping pl to %d songs" % length )
   __player.cropPlaylist(length)

def getPosition():
   # returning as a percentage value
   try:
      return (int(__player.position()), 100)
   except TypeError:
      log.msg("%r was not a valid number" % __player.position)
      return 0

def getSong():
   return __player.currentSong()

def queue(filename):
   global songStarted
   log.msg( "[Icecast] received a queue (%s)" % filename )
   if getSetting('sys_utctime', 0) == 0:
      songStarted = datetime.utcnow()
   else:
      songStarted = datetime.now()
   return __player.queue(filename)

def skipSong():
   log.msg( "[Icecast] received a skip request" )
   return __player.skip()

def stopPlayback():
   __player.stop()
   if not __player.isAlive():
      __player.join()

def pausePlayback():
   pass

def startPlayback():
   if not __player.isAlive():
      __player.start()

def status():
   return __player.status()

