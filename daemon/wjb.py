#!/usr/bin/python

import threading
import time
## import tagpy
import socket, logging, logging.handlers
from model import *
import os, sys

def getSetting(param_in):
   return Settings.byParam(param_in).value

class Player:

   def queue(self, filename):
      raise NotImplementedError, "Mus override this method"

class MPD(Player):

   __connection = None

   def __init__(self):
      # set up the connection to the daemon
      self.__connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.__connection.connect(
            ( getSetting('mpd_host'),int(getSetting('mpd_port')))
            )

   def __del__(self):
      if self.__connection is not None:
         self.__connection.close()

   def queue(self, filename):
      #note#
      # with MPD, filenames are relative to the path specified in the mpd
      # config!! This should be handled here.
      try:
         self.__connection.send(u'add %s' % filename)
         status = self.__connection.recv(1024)
         if status.startswith('ACK'):
            logging.info('Got error from MPD: %s' % status)
      except Exception, ex:
         import traceback
         logging.critical("Unexpected error:\n%s" % traceback.format_exc())
         raise

class DJ(threading.Thread):

   __keepRunning = True

   def __init__(self):
      threading.Thread.__init__(self)
      self.setName( '%s (%s)' % (self.getName(), 'DJ') )

      # initialise the player
      playerBackend = getSetting('player')
      if playerBackend == 'mpd':
         self.__connectMPD()
      else:
         raise ValueError, 'unknown player backend'

   def __connectMPD(self):
      try:
         self.__player = MPD()
      except socket.error, ex:
         try:
            self.__player = None
            logging.error('%s, retry in 5s' % ex[1])
            time.sleep(5)
            self.__connectMPD()
         except KeyboardInterrupt:
            #todo# This only stops the connection attempt. Application will
            #todo# start up cleanly after that, but without working player
            logging.info('interrupted')
            pass

   def run(self):
      logging.info('Started DJ')
      while self.__keepRunning:
         time.sleep(int(Settings.byParam('dj_cycle').value))
      logging.info('Stopped DJ')

   def stop(self):
      self.__keepRunning = False

   def startPlayback(self):
      logging.debug('starting playback')
      return ('OK', 'OK')

   def stopPlayback(self):
      logging.debug('stopping playback')
      return ('OK', 'OK')

   def nextSong(self):
      logging.debug('skipping to next song')
      return ('OK', 'OK')

   def pausePlayback(self):
      logging.debug('pausing playback')
      return ('OK', 'OK')

class Librarian(threading.Thread):

   __keepRunning = True

   def __init__(self):
      threading.Thread.__init__(self)
      self.setName( '%s (%s)' % (self.getName(), 'Lib') )

   def __crawl_directory(self, dir):
      file_id = 0
      logging.debug("scanning %s" % (dir))
      recognizedTypes = getSetting('recognizedTypes').split()
      for root, dirs, files in os.walk(dir):
         for name in files:
            if name.split('.')[-1] in recognizedTypes:
               # we have a valid file
               print os.path.join(root, name)
##               try:
##                  track = Track.getBy(Track.q.filename=filename)
##               except:
##                  track = Track(filename = os.path.join(root, name))
##                  f = tagpy.FileRef(track.filename)
##                  track.artist = f.tag().artist()
##                  track.album  = f.tag().album()
##                  track.track  = f.tag().track()
##                  track.title  = f.tag().title()
##                  track.genre  = f.tag().genre()
      logging.debug("done scanning")

   def run(self):
      logging.info('Started Librarian')
      while self.__keepRunning:
         time.sleep(int(Settings.byParam('librarian_cycle').value))
      logging.info('Stopped Librarian')

   def stop(self):
      self.__keepRunning = False

   def rescan(self):
      for mediaFolder in list(list(Settings.selectBy(param='folder'))):
         print mediaFolder.value
         threading.Thread(target=self.__crawl_directory, kwargs={'dir': mediaFolder.value}).start()
         ##self.__crawl_directory(mediaFolder.value)

   def detect_moves(self):
      logging.debug("detecting moves")

   def detect_orphans(self):
      logging.debug("detecting orphans")
      pass

   def find_duplicates(self):
      logging.debug("searching for duplicates")
      pass

   def add_file(self, filename):
      logging.debug("adding file %s" % (filename))
      pass

   def read_metadata(self, filename):
      logging.debug("reading metadata from %s" % (filename))
      pass

   def find_cover_art(self, artist, album):
      logging.debug("finding cover art for %s %s" % (artist, album))
      pass

   def mark_dirty(self, songID):
      logging.info("marking %s as dirty" % (songID))
      try:
         Songs.get(int(songID)).dirty = True
         return (True, 'OK')
      except Exception, ex:
         return (False, str(ex))

class Arbitrator(threading.Thread):

   global lib

   def __init__(self, connection, address):
      self.__connection = connection
      self.__address    = address
      threading.Thread.__init__(self)
      self.setName( '%s (%s)' % (self.getName(), 'Arb') )

   def dispatch(self, command):

      try:
         #
         # Library commands
         #
         if command == 'rescanlib':
            lib.rescan()
            lib.detect_moves()    # after importing, we can detect moves
            lib.detect_orphans()  # everything in the db that has no file on HD and did not move is orphanded and should be removed from the DB
            lib.find_duplicates() # Now we can search for duplicates
            return 'OK:DEFERRED\n'
##         elif command.split()[0] == 'addfile':
##            lib.add_file(command.split()[1])
##            return 'OK:OK\n'
##         elif command.split()[0] == 'readmeta':
##            lib.read_metadata(command.split()[1])
##            return 'OK:OK\n'
##         elif command.split()[0] == 'findcover':
##            lib.find_cover_art(command.split()[1])
##            return 'OK:OK\n'
         elif command.split()[0] == 'markdirty':
            res = lib.mark_dirty(command.split()[1])
            if res[0]: return 'OK:%s\n' % res[1]
            else: return 'ER:%s\n' % res[1]
         #
         # DJ commands
         #
         elif command == 'play':
            res = dj.startPlayback()
            if res[0]: return 'OK:%s\n' % res[1]
            else: return 'ER:%s\n' % res[1]
         elif command == 'pause':
            res = dj.pausePlayback()
            if res[0]: return 'OK:%s\n' % res[1]
            else: return 'ER:%s\n' % res[1]
         elif command == 'stop':
            res = dj.stopPlayback()
            if res[0]: return 'OK:%s\n' % res[1]
            else: return 'ER:%s\n' % res[1]
         elif command == 'skip':
            res = dj.nextSong()
            if res[0]: return 'OK:%s\n' % res[1]
            else: return 'ER:%s\n' % res[1]
         #
         # Unknown commands
         #
         else:
            logging.info("received unknown command: %s" % command)
            return 'ER:UNKNOWN COMMAND\n'
      except Exception, ex:
         import traceback
         logging.critical("Unexpected error:\n%s" % traceback.format_exc())
         return "ER:%s\n" % ex

   def run(self):
      logging.debug( "Arbitrator awaiting your commands" )
      self.__connection.send('HELLO\n')
      while True:
         data = self.__connection.recv(1024)[0:-1]
         if data:
            logging.info( "command from %s: %s" % (self.__address[0], data) )
            self.__connection.send(self.dispatch(data))
         else:
            break
      self.__connection.send('BYE\n')
      self.__connection.close()
      logging.debug( "Arbitrator quit" )

if __name__ == "__main__":

   logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(levelname)-8s %(threadName)-15s %(message)s')
   formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s %(threadName)-15s %(message)s')
   rotfile = logging.handlers.RotatingFileHandler('wjb.log', maxBytes=100*1024, backupCount=3)
   rotfile.setLevel(logging.DEBUG)
   rotfile.setFormatter(formatter)
   logging.getLogger('').addHandler(rotfile)

   # if the table does not exist, create it.
   try:
      CommandQueue.createTable()
      pass
   except Exception, ex:
      if ex[0] == 1050: # table exists
         pass
      else:
         logging.error(ex)
         raise

   host = getSetting('daemon_iface')
   port = int(getSetting('daemon_port'))

   # Start the agents
   lib = Librarian(); lib.start()

   dj = None
   try:
      dj = DJ()
   except ValueError, ex:
      if str(ex) == 'unknown player backend':
         logging.error('Unknown player specified in the config')
         lib.stop(); lib.join()
         sys.exit(0)
   else:
      dj.start()


   sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
   sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   sock.bind((host, port))
   sock.listen(5)
   logging.info( "===== WJB Deamon started up ===============" )
   logging.info( "listening on %s:%s" % (host, port) )

   while True:
      try:
         # wait for next client to connect
         connection, address = sock.accept()
         logging.info( "accepting incoming connection from %s" % (address[0]) )
         t = Arbitrator(connection, address)
         t.start()
      except KeyboardInterrupt:
         logging.info( "----- Waiting for agents to stop ----------" )
         lib.stop(); lib.join()
         dj.stop();  dj.join()
         logging.info( "===== WJB Deamon shutdown =================" )
         break

