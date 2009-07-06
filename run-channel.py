#!/usr/bin/python
"""
Run a specific jukebox channel
"""
import os, sys
import signal
import logging
import logging.config
from pydata.channel import Channel
logger = logging.getLogger(__name__)
logging.config.fileConfig("logging.ini")
CHANNEL = None

class Watcher(object):
   def __init__(self):
      """ Creates a child thread, which returns.  The parent
          thread waits for a KeyboardInterrupt and then kills
          the child thread.
      """
      self.child = os.fork()
      if self.child == 0:
          return
      else:
          self.watch()

   def watch(self):
       try:
           os.wait()
       except KeyboardInterrupt:
           # I put the capital B in KeyBoardInterrupt so I can
           # tell when the Watcher gets the SIGINT
           print 'KeyBoardInterrupt'
           self.kill()
       sys.exit()

   def kill(self):
       try:
           os.kill(self.child, signal.SIGKILL)
       except OSError:
          pass

def run_channel( channel_name ):
   "Starts a channel"
   from pydata.channel import Channel
   CHANNEL = Channel( channel_name )
   if CHANNEL:
      logging.info( "Starting channel %s" % channel_name )
      CHANNEL.startPlayback()
      try:
         CHANNEL.run()
      except:
         import traceback
         traceback.print_exc()
         sys.exit(0)
   else:
      logging.critical( "Unable to load (or find) channel %s" % channel_name )

def main():
   """
   Parse command line options, bootstrap the app and run the channel
   """
   from optparse import OptionParser

   parser = OptionParser()
   parser.add_option("-c", "--channel", dest="channel_name",
      help="runs the channel named CHANNEL_NAME", metavar="CHANNEL_NAME")
   parser.add_option("-v", action="count", dest="verbosity", help="Application verbosity. Can be repeated up to 5 times, each time increasing verbosity). If not set, the logging configuration file will take precedence.")

   (options, args) = parser.parse_args()

   if not options.channel_name:
      parser.error( "CHANNEL_NAME is required!" )

   verbosity_map = {
         5: logging.DEBUG,
         4: logging.INFO,
         3: logging.WARN,
         2: logging.ERROR,
         1: logging.CRITICAL,
         }
   if options.verbosity and options.verbosity in verbosity_map:
      logger.setLevel( verbosity_map[ options.verbosity ] )
   elif options.verbosity and options.verbosity > len(verbosity_map):
      logger.setLevel( logging.DEBUG )

   run_channel( options.channel_name )

if __name__ == "__main__":
   main()
