import os
import re
from datetime import datetime
import thread
import time
import logging
import urllib2
from hashlib import md5

import pygst
pygst.require("0.10")
import gst
from demon.dbmodel import State

LOG = logging.getLogger(__name__)

class PlayerState(object):
    def __init__(self):
        self.song_started = None
        self.admin_password = None
        self.admin_url = None
        self.admin_user = None
        self.channel_id = 0
        self.mount = None
        self.password = None
        self.port = None
        self.queue = []
        self.server = None
        #self.loop = None

class GStreamer(object):

    def __init__(self):
        self.player = None
        self.filename = None
        self.is_playing = False
        self.method = "module_method"
        LOG.info("GStreamer class initialised")
        self.init_player()

    def init_player(self):
        LOG.debug("Initialising the player...")
        self.player = gst.Pipeline( "player" )
        source = gst.element_factory_make( "filesrc", "file-source" )
        decoder = gst.element_factory_make( "mad", "mp3-decoder" )
        conv = gst.element_factory_make( "audioconvert", "converter" )
        encoder = gst.element_factory_make( "lamemp3enc", "encoder" )
        resampler = gst.element_factory_make( "audioresample", "resampler" )
        tagger = gst.element_factory_make( "taginject", "tagger" )
        icysource = gst.element_factory_make( "shout2send", "icysource" )
        self.player.add( source, decoder, conv, resampler, encoder, tagger, icysource )
        gst.element_link_many( source, decoder, conv, encoder, icysource )
        bus = self.player.get_bus()
        LOG.debug("Async message bus: %r" % bus)
        bus.add_signal_watch()
        bus.connect( "message", self.on_message )

    def current_position(self):
        try:
            return ( int(self.player.query_position(gst.FORMAT_TIME, None)[0] * 1E-9),
                     int(self.player.query_duration(gst.FORMAT_TIME, None)[0] * 1E-9))
        except Exception, exc:
            LOG.error(exc)
            return (0, 100)

    def on_message( self, bus, message ):
        """
        gstramer callback.

        gstreamer calls this method from time to time sending additional
        payload along the "message" parameter
        """
        LOG.warning("--------------------------- MESSAGE -----------------")
        if message.type == gst.MESSAGE_EOS:
            LOG.debug("End of stream reached")
            self.player.set_state( gst.STATE_NULL )
            self.is_playing = False
            #STATE.loop.quit()
        elif message.type == gst.MESSAGE_ERROR:
            self.player.set_state( gst.STATE_NULL )
            err, debug = message.parse_error()
            LOG.error( "Error: %s" % err )
            LOG.debug( "Debug info: %s" % debug )
            self.is_playing = False
        else:
            LOG.debug( "Unexpected gst message: %s" %  message )

    def stop(self):
        LOG.info("Stopping stream")
        self.filename = None
        self.player.set_state(gst.STATE_NULL)
        self.is_playing = False

    def status(self):
        return self.is_playing and "playing" or "stop"

    def start_stop(self, filename):
        if self.is_playing:
            self.stop()
        else:
            LOG.info("Stream startin for %s" % filename)
            self.filename = filename
            if not os.path.isfile( filename ):
                LOG.error( "%r is not a file!" % filename )
                return

            self.player.get_by_name("file-source").set_property( "location", filename)
            thread.start_new_thread( self.play, () )

    def play( self ):
        self.player.get_by_name("encoder").set_property("bitrate", 128)
        self.player.get_by_name("tagger").set_property("tags", "album=testalbum,title=testtitle,artist=testartist")
        self.player.get_by_name("icysource").set_property("ip", "127.0.0.1")
        self.player.get_by_name("icysource").set_property("port", STATE.port)
        self.player.get_by_name("icysource").set_property("password", STATE.password)
        self.player.get_by_name("icysource").set_property("mount", STATE.mount)
        self.player.get_by_name("icysource").set_property("streamname", "The Wicked Jukebox - test.mp3")
        self.player.set_state( gst.STATE_PLAYING)
        self.is_playing = True
        #while self.is_playing:
        #    try:
        #        self.position = (
        #            int(self.player.query_position(gst.FORMAT_TIME, None)[0] * 1E-9),
        #            int(self.player.query_duration(gst.FORMAT_TIME, None)[0] * 1E-9),
        #        )
        #        LOG.debug("Current position: %r/%r " % self.position)
        #    except Exception, exc:
        #        self.position = (0, 0)
        #        LOG.error(exc)
        #    time.sleep(1)
        #STATE.loop.quit()

def config(params):
   LOG.info( "connection to icecast server (params = %s)" % params )
   STATE.port     = int(params['port'])
   STATE.mount    = str(params['mount'])
   STATE.password = str(params['pwd'])
   STATE.channel_id = int(params['channel_id'])

   if "admin_url" in params:
      STATE.admin_url = str(params["admin_url"]) + "/listclients.xsl?mount=" + STATE.mount

   if "admin_username" in params:
      STATE.admin_username = str(params["admin_username"])

   if "admin_password" in params:
      STATE.admin_password = str(params["admin_password"])

def getPosition():
    if not STATE.server:
        output = (0, 100)
    else:
        output = STATE.server.current_position()
    State.set("progress", output[0], STATE.channel_id)
    return output

def getSong():
    if STATE.server:
        return STATE.server.filename
    return None

def queue(filename):
   from demon.dbmodel import Setting
   LOG.debug( "Received a queue (%s)" % filename )
   if Setting.get('sys_utctime', 0) == 0:
      STATE.song_started = datetime.utcnow()
   else:
      STATE.song_started = datetime.now()

   STATE.queue.append( filename )

def cropPlaylist(length=2):
   """
   Removes items from the *beginning* of the playlist to ensure it has only
   a fixed number of entries.

   @type  length: int
   @param length: The new size of the playlist
   """
   LOG.debug( "Cropping pl to %d songs" % length )
   if len( STATE.queue ) <= length:
      return True

   STATE.queue = STATE.queue[-length:]
   return True

def skipSong():
   LOG.debug( "Received a skip request" )
   stopPlayback()
   startPlayback()

def stopPlayback():
   from demon.dbmodel import State

   LOG.debug( "Stopping playback" )
   if STATE.server:
      STATE.server.stop()

   State.set("progress", 0, STATE.channel_id)
   LOG.debug( "Playback stopped" )

def pausePlayback():
   pass

def startPlayback():
   from demon.dbmodel import State

   LOG.info( "Starting playback" )
   State.set("progress", 0, STATE.channel_id)
   if not STATE.queue:
      LOG.warn( "Nothing on queue." )
      return False

   if not STATE.server:
      import sys
      LOG.warn( "No icecast connection available!" )
      STATE.server = GStreamer()

   STATE.server.start_stop(STATE.queue.pop(0))
   #gobject.threads_init()
   #STATE.loop = glib.MainLoop()
   #STATE.loop.run()

def status():
   if STATE.server:
      return STATE.server.status()
   else:
      return "stopped"

def current_listeners():
   """
   Scrape the Icecast admin page for current listeners and return a list of
   MD5 hashes of their IPs
   """

   if STATE.admin_url is None or \
      STATE.admin_username is None or \
      STATE.admin_password is None :
      # not all required backend parameters supplied
      LOG.warning( "Not all parameters set for screen scraping icecast statistics. Need admin-url and admin-password" )
      return

   part = "25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]?"
   p = re.compile(r"(((%s)\.){3}(%s))" % (part, part))

   # Create an OpenerDirector with support for Basic HTTP Authentication...
   auth_handler = urllib2.HTTPBasicAuthHandler()
   auth_handler.add_password(realm='Icecast2 Server',
                             uri=STATE.admin_url,
                             user=STATE.admin_username,
                             passwd=STATE.admin_password)
   opener = urllib2.build_opener(auth_handler)
   # ...and install it globally so it can be used with urlopen.
   urllib2.install_opener(opener)

   try:
      LOG.debug("Opening %r" % STATE.admin_url)
      handler = urllib2.urlopen(STATE.admin_url)
      data = handler.read()

      listeners = [md5(x[0]).hexdigest() for x in p.findall(data)]
      return listeners
   except urllib2.HTTPError, ex:
      LOG.error("Error opening %r: Caught %r" % (STATE.admin_url, str(ex)))
      return None
   except urllib2.URLError, ex:
      LOG.error("Error opening %r: Caught %r" % (STATE.admin_url, str(ex)))
      return None

STATE = PlayerState()

if __name__ == "__main__":
    import sys
    from getpass import getpass
    logging.basicConfig(level=logging.DEBUG)
    LOG.info("Streaming %r to icecast..." % sys.argv[1])

    params = {}
    params['port'] = int(raw_input("ICY port: "))
    params['mount'] = raw_input("ICY Mount: ")
    params['pwd'] = getpass("ICY Passwd: ")
    params['channel_id'] = int(raw_input("Channel ID: "))
    config(params)
    obj = GStreamer()
    obj.start_stop(sys.argv[1])
    #gobject.threads_init()
    #STATE.loop = glib.MainLoop()
    #STATE.loop.run()

