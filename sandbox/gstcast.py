import sys
import os
import thread
import glib
import gobject
import pygst
pygst.require("0.10")
import gst
import time

PLAYER = None
IS_PLAYING = False
METHOD = "module_method"

def on_message( bus, message ):
   global IS_PLAYING
   if message.type == gst.MESSAGE_EOS:
      print "EOS reached"
      PLAYER.set_state( gst.STATE_NULL )
      IS_PLAYING = False
   elif message.type == gst.MESSAGE_ERROR:
      PLAYER.set_state( gst.STATE_NULL )
      err, debug = message.parse_error()
      print "Error: %s" % err
      print "Debug info: %s" % debug
      IS_PLAYING = False
   else:
      print message

def play( filename, icy_passwd ):
   global IS_PLAYING
   if not os.path.isfile( filename ):
      print "%r is not a file!" % filename
      return

   PLAYER.get_by_name("file-source").set_property(
         "location", filename)
   PLAYER.get_by_name("encoder").set_property("bitrate", 128)
   PLAYER.get_by_name("tagger").set_property("tags", "album=testalbum,title=testtitle,artist=testartist")
   PLAYER.get_by_name("icysource").set_property("ip", "127.0.0.1")
   PLAYER.get_by_name("icysource").set_property("port", 8001)
   PLAYER.get_by_name("icysource").set_property("password", icy_passwd)
   PLAYER.get_by_name("icysource").set_property("mount", "wicked.mp3")
   PLAYER.get_by_name("icysource").set_property("streamname", "The Wicked Jukebox - wicked.mp3")
   PLAYER.set_state( gst.STATE_PLAYING)
   IS_PLAYING = True
   while IS_PLAYING:
      time.sleep(1)
   LOOP.quit()

def init_player():
   global PLAYER
   PLAYER = gst.Pipeline( "player" )
   source = gst.element_factory_make( "filesrc", "file-source" )
   decoder = gst.element_factory_make( "mad", "mp3-decoder" )
   conv = gst.element_factory_make( "audioconvert", "converter" )
   encoder = gst.element_factory_make( "lamemp3enc", "encoder" )
   resampler = gst.element_factory_make( "audioresample", "resampler" )
   tagger = gst.element_factory_make( "taginject", "tagger" )
   icysource = gst.element_factory_make( "shout2send", "icysource" )
   PLAYER.add( source, decoder, conv, resampler, encoder, tagger, icysource )
   gst.element_link_many( source, decoder, conv, encoder, icysource )
   bus = PLAYER.get_bus()
   bus.add_signal_watch()
   bus.connect( "message", on_message )

# gstreamer chain:
#
# filesrc location=<filename>
# mad
# audioconvert
# lame bitrate=128
# taginject tags="title=<title>,artist=<artist>,album=<album>"
# shout2send ip=<ip> port=<pors> password=<pwd> mount=<mount> streamname=<streamname>

if __name__ == "__main__":
   from getpass import getpass
   init_player()
   source_pwd = getpass("Icecast source password: ")
   thread.start_new_thread( play, ( sys.argv[1], source_pwd) )
   gobject.threads_init()
   LOOP = glib.MainLoop()
   LOOP.run()

