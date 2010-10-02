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

class CLI_Main:

   def __init__(self):
      self.player = gst.element_factory_make( "playbin2", "player" )
      fakesink = gst.element_factory_make( "fakesink", "fakesink" )
      self.player.set_property( "video-sink", fakesink )
      bus = self.player.get_bus()
      bus.add_signal_watch()
      bus.connect( "message", self.on_message )
      self.is_playing = False

   def on_message( self, bus, message ):
      if message.type == gst.MESSAGE_EOS:
         print "EOS reached"
         self.player.set_state( gst.STATE_NULL )
         self.is_playing = False
      elif message.type == gst.MESSAGE_ERROR:
         self.player.set_state( gst.STATE_NULL )
         err, debug = message.parse_error()
         print "Error: %s" % err
         print "Debug info: %s" % debug
         self.is_playing = False

   def start(self):
      filename = sys.argv[1]
      if not os.path.isfile( filename ):
         print "%r is not a file!" % filename
         return

      self.is_playing = True
      self.player.set_property( "uri", "file://%s" + filename )
      self.player.set_state( gst.STATE_PLAYING)
      while self.is_playing:
         time.sleep(1)
      LOOP.quit()

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

def play( filename ):
   global IS_PLAYING
   if not os.path.isfile( filename ):
      print "%r is not a file!" % filename
      return

   IS_PLAYING = True

   fakesink = gst.element_factory_make( "fakesink", "fakesink" )
   PLAYER.set_property( "video-sink", fakesink )
   bus = PLAYER.get_bus()
   bus.add_signal_watch()
   bus.connect( "message", on_message )

   PLAYER.set_property( "uri", "file://%s" + filename )
   PLAYER.set_state( gst.STATE_PLAYING)
   while IS_PLAYING:
      time.sleep(1)
   LOOP.quit()

if __name__ == "__main__":
   if METHOD == "cli_object":
      cli = CLI_Main()
      thread.start_new_thread( cli.start, () )
   else:
      PLAYER = gst.element_factory_make( "playbin2", "player" )
      thread.start_new_thread( play, (sys.argv[1],) )
   gobject.threads_init()
   LOOP = glib.MainLoop()
   LOOP.run()

