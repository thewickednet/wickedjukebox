import os
import thread
import time
import logging

import glib
import gobject
import pygst
pygst.require("0.10")
import gst

LOG = logging.getLogger(__name__)

__PORT = None
__MOUNT = None
__PASSWORD = None
__STREAMER = None
__ADMIN_URL = None
__ADMIN_USER = None
__ADMIN_PASSWORD = None
__CHANNEL_ID = 0

class GStreamer(object):

    def __init__(self, passwd):
        self.position = (0,0)
        self.player = None
        self.thread_id = None
        self.icy_passwd = passwd
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
        bus.add_signal_watch()
        bus.connect( "message", self.on_message )

    def current_position(self):
        pass

    def on_message( self, bus, message ):
        """
        gstramer callback.

        gstreamer calls this method from time to time sending additional
        payload along the "message" parameter
        """
        if message.type == gst.MESSAGE_EOS:
            LOG.debug("End of stream reached")
            self.player.set_state( gst.STATE_NULL )
            self.is_playing = False
        elif message.type == gst.MESSAGE_ERROR:
            self.player.set_state( gst.STATE_NULL )
            err, debug = message.parse_error()
            LOG.error( "Error: %s" % err )
            LOG.debug( "Debug info: %s" % debug )
            self.is_playing = False
        else:
            LOG.debug( "Unexpected gst message: %s" %  message )

    def start_stop(self, filename):
        if self.is_playing:
            LOG.info("Stopping stream")
            self.thread_id = None
            self.player.set_state(gst.STATE_NULL)
            self.is_playing = False
        else:
            LOG.info("Stream startin for %s" % filename)
            if not os.path.isfile( filename ):
                LOG.error( "%r is not a file!" % filename )
                return

            self.player.get_by_name("file-source").set_property( "location", filename)
            self.thread_id = thread.start_new_thread( self.play, () )

    def play( self ):
        self.player.get_by_name("encoder").set_property("bitrate", 128)
        self.player.get_by_name("tagger").set_property("tags", "album=testalbum,title=testtitle,artist=testartist")
        self.player.get_by_name("icysource").set_property("ip", "127.0.0.1")
        self.player.get_by_name("icysource").set_property("port", 8001)
        self.player.get_by_name("icysource").set_property("password", self.icy_passwd)
        self.player.get_by_name("icysource").set_property("mount", "test.mp3")
        self.player.get_by_name("icysource").set_property("streamname", "The Wicked Jukebox - test.mp3")
        self.player.set_state( gst.STATE_PLAYING)
        self.is_playing = True
        while self.is_playing:
            try:
                self.position = (
                    int(self.player.query_position(gst.FORMAT_TIME, None)[0] * 1E-9),
                    int(self.player.query_duration(gst.FORMAT_TIME, None)[0] * 1E-9),
                )
                LOG.debug("Current position: %r/%r " % self.position)
            except Exception, exc:
                self.position = (0, 0)
                LOG.error(exc)
            time.sleep(1)
        LOOP.quit()

def config(params):
   global __PORT, __MOUNT, __PASSWORD, __STREAMER, __ADMIN_URL, __ADMIN_USER, __ADMIN_PASSWORD, __CHANNEL_ID
   LOG.info( "connection to icecast server (params = %s)" % params )
   __PORT     = int(params['port'])
   __MOUNT    = str(params['mount'])
   __PASSWORD = str(params['pwd'])
   __CHANNEL_ID = int(params['channel_id'])

   if "admin_url" in params:
      __ADMIN_URL = str(params["admin_url"]) + "/listclients.xsl?mount=" + __MOUNT

   if "admin_username" in params:
      __ADMIN_USER = str(params["admin_username"])

   if "admin_password" in params:
      __ADMIN_PASSWORD = str(params["admin_password"])

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

   Return "None" if this feature is not supported or if the list of listeners is unknown
   """
   return []

if __name__ == "__main__":
    import sys
    from getpass import getpass
    logging.basicConfig(level=logging.DEBUG)
    LOG.info("Streaming %r to icecast..." % sys.argv[1])

    source_pwd = getpass("Icecast source password: ")
    obj = GStreamer(source_pwd)
    obj.start_stop(sys.argv[1])
    gobject.threads_init()
    LOOP = glib.MainLoop()
    LOOP.run()

