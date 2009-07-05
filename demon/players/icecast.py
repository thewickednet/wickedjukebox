import os
import threading
from datetime import datetime
from demon.dbmodel import Setting, State
from pydata.util import fsdecode
import mutagen
import shout
import time
import urllib2
import re
from hashlib import md5

import logging
LOG = logging.getLogger(__name__)

STATUS_STOPPED = 1
STATUS_PLAYING = 2
STATUS_PAUSED  = 3

class Shoutcast_Player(threading.Thread):

   def __init__(self, password='hackme', mount='/wicked.mp3', port=8000, name="The wicked jukebox", url="http://jukebox.wicked.lu", bufsize=1024, bitrate=128, samplerate=44100, channels=1, channel_id=0 ):
      self.__keepRunning      = True
      self.__progress         = (0, 0) # (streamed_bytes, total_bytes)
      self.__queue            = []
      self.__currentSong      = u''
      self.__triggerSkip      = False
      self.__status           = STATUS_STOPPED
      self.__bufsize          = bufsize
      self.__port             = port
      self.__password         = password
      self.__mount            = mount
      self.__ai_bitrate       = str(bitrate)
      self.__ai_samplerate    = str(samplerate)
      self.__ai_channels      = str(channels)
      self.__name             = name
      self.__url              = url
      self.__channel_id       = channel_id
      self.connect()
      threading.Thread.__init__(self)

   def disconnect_server(self):
      self.__status = STATUS_STOPPED
      State.set("progress", 0, self.__channel_id)
      self.__server.close()

   def connect(self):
      self.__server           = shout.Shout()
      self.__server.format    = 'mp3'
      self.__server.audio_info = { "bitrate": self.__ai_bitrate, "samplerate": self.__ai_samplerate, "channels": self.__ai_channels }
      self.__server.user      = "source"
      self.__server.name      = self.__name
      self.__server.url       = self.__url
      self.__server.password  = self.__password
      self.__server.mount     = self.__mount
      self.__server.port      = self.__port
      self.__server.nonblocking = False
      self.__server.open()

   def reconnect(self):
      try:
         self.disconnect_server()
      except:
         pass
      self.connect()

   def get_description(self, filename):
      artist = "unkown artist"
      title =  "unknown song"
      try:
         meta = mutagen.File( filename )
         if meta.has_key( 'TPE1' ):
            artist = meta.get( 'TPE1' ).text[0]
         elif meta.has_key( 'artist' ):
            artist = meta.get('artist')[0]

         if meta.has_key( 'TIT2' ):
            title = meta.get( 'TIT2' ).text[0]
         elif meta.has_key( 'title' ):
            title = meta.get('title')[0]
      except Exception, ex:
         import traceback
         LOG.error( "%s contained no valid metadata!" % filename )
         traceback.print_exc()
      return "%s - %s" % (artist, title)

   def run(self):

      while self.__keepRunning is True:

         if len(self.__queue) > 0:
            self.__currentSong = self.__queue.pop(0)
            self.__bufsize = int(Setting.get('icecast_bufsize', 1024))

            f = open(self.__currentSong, "rb")

            self.__server.set_metadata({"song": self.get_description(self.__currentSong).encode("utf-8")})
            buf = f.read(self.__bufsize)
            self.__progress = (0, os.stat(self.__currentSong).st_size)
            State.set("progress", 0, self.__channel_id)
            self.__status = STATUS_PLAYING

            # stream the file as long as the player is running, or as long as
            # it's not skipped
            count = 0 # loop count (used to set the progress not on every sent buffer)
            while not self.__triggerSkip and self.__keepRunning and buf:

               while self.__keepRunning is True:
                  try:
                     self.__server.send(buf)
                     if self.__server.nonblocking:
                        while self.__server.queuelen() > 1:
                           pass
                     self.__server.sync()
                     break
                  except RuntimeError, ex:
                     # for shoutpy module
                     import traceback
                     traceback.print_exc()
                     if (str(ex).find("Socket error") > -1):
                        time.sleep(1)
                        LOG.warning("Socket error! Reconnecting...")
                        self.reconnect()
                     else:
                        raise
                  except shout.ShoutException, ex:
                     # for shout module
                     import traceback
                     traceback.print_exc()
                     if (str(ex).find("Socket error") > -1):
                        time.sleep(1)
                        LOG.warning("Socket error! Reconnecting...")
                        self.reconnect()
                     else:
                        raise

               self.__progress = (self.__progress[0]+len(buf),
                                  self.__progress[1])
               count += 1
               if count % 30 == 0:
                  State.set("progress", self.position(), self.__channel_id)
               buf = f.read(self.__bufsize)
            f.close()

            LOG.debug( "Shoutcast song finished" )
            self.__status = STATUS_STOPPED
            State.set("progress", 0, self.__channel_id)

            # if we fell through the previous loop because a skip was
            # requested, we need to reset that value. Otherwise we keep
            # skipping
            if self.__triggerSkip:
               self.__triggerSkip = False

      LOG.debug("Shoutcast loop finished")
      State.set("progress", 0, self.__channel_id)

      self.disconnect_server()
      self.__status = STATUS_STOPPED

   def skip(self):
      LOG.debug( "Shoutcast player got a skip request" )
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
         import traceback
         traceback.print_exc()
         return 0

   def pause(self):
      pass

   def stop(self):
      LOG.debug( "Shoutcast player got a stop request" )
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

__port     = None
__mount    = None
__password = None
__player   = None
__adminurl = None
__adminuser = None
__adminpassword = None
__channel_id = 0
songStarted = None

def config(params):
   global __port, __mount, __password, __player, __adminurl, __adminuser, __adminpassword, __channel_id
   LOG.info( "connection to icecast server (params = %s)" % params )
   __port     = int(params['port'])
   __mount    = str(params['mount'])
   __password = str(params['pwd'])
   __channel_id = int(params['channel_id'])
   __player   = Shoutcast_Player(__password,
                                 __mount,
                                 __port,
                                 channel_id=__channel_id)

   if "admin_url" in params:
      __adminurl = str(params["admin_url"]) + "/listclients.xsl?mount=" + __mount

   if "admin_username" in params:
      __adminuser = str(params["admin_username"])

   if "admin_password" in params:
      __adminpassword = str(params["admin_password"])

def cropPlaylist(length=2):
   """
   Removes items from the *beginning* of the playlist to ensure it has only
   a fixed number of entries.

   @type  length: int
   @param length: The new size of the playlist
   """
   LOG.debug( "[Icecast] cropping pl to %d songs" % length )
   __player.cropPlaylist(length)

def getPosition():
   # returning as a percentage value
   try:
      return (int(__player.position()), 100)
   except TypeError:
      import traceback
      traceback.print_exc()
      LOG.warning("%r was not a valid number" % __player.position)
      return 0

def getSong():
   return __player.currentSong()

def queue(filename):
   global songStarted
   LOG.debug( "[Icecast] received a queue (%s)" % filename )
   if Setting.get('sys_utctime', 0) == 0:
      songStarted = datetime.utcnow()
   else:
      songStarted = datetime.now()
   return __player.queue(filename)

def skipSong():
   LOG.debug( "[Icecast] received a skip request" )
   return __player.skip()

def stopPlayback():
   __player.stop()
   if not __player.isAlive():
      __player.join()

def pausePlayback():
   pass

def startPlayback():
   print "Starting playback"
   if not __player.isAlive():
      try:
         __player.start()
      except AssertionError, e:
         import traceback
         traceback.print_exc()
         LOG.error(e)
         stopPlayback()
      except RuntimeError, e:
         import traceback
         traceback.print_exc()
         if (str(e).find("thread already started") > -1):
            pass
         else:
            raise

def status():
   return __player.status()

def current_listeners():
   """
   Scrape the Icecast admin page for current listeners and return a list of
   MD5 hashes of their IPs
   """

   if __adminurl is None or \
      __adminuser is None or \
      __adminpassword is None :
      # not all required backend parameters supplied
      print "Not all parameters set for screen scraping icecast statistics"
      return

   part = "25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]?"
   p = re.compile(r"(((%s)\.){3}(%s))" % (part, part))

   # Create an OpenerDirector with support for Basic HTTP Authentication...
   auth_handler = urllib2.HTTPBasicAuthHandler()
   auth_handler.add_password(realm='Icecast2 Server',
                             uri=__adminurl,
                             user=__adminuser,
                             passwd=__adminpassword)
   opener = urllib2.build_opener(auth_handler)
   # ...and install it globally so it can be used with urlopen.
   urllib2.install_opener(opener)

   try:
      LOG.debug("Opening %r" % __adminurl)
      handler = urllib2.urlopen(__adminurl)
      data = handler.read()

      listeners = [md5(x[0]).hexdigest() for x in p.findall(data)]
      return listeners
   except urllib2.HTTPError, ex:
      LOG.error("Error opening %r: Caught %r" % (__adminurl, str(ex)))
      return None
   except urllib2.URLError, ex:
      LOG.error("Error opening %r: Caught %r" % (__adminurl, str(ex)))
      return None
