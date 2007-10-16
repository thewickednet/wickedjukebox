import os
import threading
from twisted.python import log
import shoutpy

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
      self.__server.open()
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
      # TODO: do some real calculations with bitrate (CBR & VBR) to return the
      #       position in seconds!
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

# ----------------------------------------------------------------------------

__port     = None
__mount    = None
__password = None
__player   = None

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
   return (int(__player.position), 100)

def getSong():
   return __player.currentSong()

def queue(filename):
   log.msg( "[Icecast] received a queue (%s)" % filename )
   return __player.queue(filename)

def skipSong():
   log.msg( "[Icecast] received a skip request" )
   return __player.skip()

def stopPlayback():
   __player.stop()

def pausePlayback():
   pass

def startPlayback():
   __player.start()

def status():
   pass

