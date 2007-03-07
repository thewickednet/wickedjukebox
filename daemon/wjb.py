#!/usr/bin/python
#
# -----------------------------------------------------------------------------
#  $Id$
# -----------------------------------------------------------------------------
#  This file contains all the agents and the main program. It is executable.
#  Once it's executed it will start up two worker threads and listen for
#  network connections. No daemon mode is available yet to simplify debugging.
# -----------------------------------------------------------------------------

import threading
import time, md5
import kaa.metadata, kaa.strutils
import logging, logging.handlers, logging.config
import socket
from model import *
import os, sys
from sqlobject.sqlbuilder import *
from MySQLdb import OperationalError
from datetime import datetime
from demon import Juggler
from util import *
import urllib, httplib

class Librarian(threading.Thread):
   """
   The librarian is a worker thread that manages the music library
   """

   __activeScans = []
   __scheduleMovesDetection  = False
   __scheduleOrphanDetection = False
   __logger        = logging.getLogger('lib')
   __keepRunning   = True

   class Scanner(threading.Thread):

      __scanLog       = logging.getLogger('lib.scanner')

      def __init__(self, folders):
         self.__folders = folders
         threading.Thread.__init__(self)

      def __crawl_directory(self, dir):
         """
         Scans a directory and all its subfolders for media files and stores their
         metadata into the library (DB)
         """

         self.__scanLog.info("-------- scanning %s ---------" % (dir))

         # Only scan the files specified in the settings table
         recognizedTypes = getSetting('recognizedTypes', 'mp3 ogg flac').split()

         # walk through the directories
         scancount  = 0
         errorCount = 0
         for root, dirs, files in os.walk(dir):
            for name in files:
               if name.split('.')[-1] in recognizedTypes:
                  # we have a valid file
                  filename = os.path.join(root,name)

                  try:
                     # parse the metadata
                     self.__scanLog.debug("Scanning %s" % filename)
                     metadata = kaa.metadata.parse(filename)

                     # if we have an artist, set the artist field.
                     # then, if we *also* have an album, store the album from this
                     # artist and set the song's metadata accordingly.
                     # Finally, the song needs a track position on that album. So
                     # we set it.
                     dbArtist = None
                     dbAlbum  = None
                     self.__scanLog.debug('   Artist is %s' % (repr(metadata.get('artist'))))
                     if metadata.get('artist') is not None:
                        dbArtist = getArtist(to_utf8(metadata.get('artist')))

                        self.__scanLog.debug('   Album is %s' % (repr(metadata.get('album'))))
                        if metadata.get('album') is not None:
                           try:
                              dbAlbum = getAlbum(
                                          to_utf8(metadata.get('artist')),
                                          to_utf8(metadata.get('album'))
                                       )
                           except Exception, ex:
                              if str(ex).upper().find("DUPLICATE") < 0:
                                 # The word "duplicate" did not appear in the
                                 # exception message. This means, some other error
                                 # happened, so we simply raise that exception
                                 # again so it can be caught separately.
                                 raise
                              else:
                                 # The word "duplicate" was found. We silently
                                 # ignore this error, but keep a log
                                 self.__scanLog.warning('Duplicate album %s - %s' % (
                                    metadata.get('artist'),
                                    metadata.get('album')))
                                 pass
                        else:
                           self.__scanLog.warning('album cannot be NULL for %s', filename)
                     else:
                        self.__scanLog.warning('artist cannot be NULL for %s', filename)

                     if metadata.get('length') is not None:
                        duration = int(metadata.get('length'))
                     else:
                        duration = 0

                     filesize = os.stat(filename).st_size

                     if metadata.get('bitrate') is not None:
                        bitrate = int(metadata.get('bitrate'))
                     else:
                        bitrate = 0

                     if metadata.get('trackno') is not None:
                        try:
                           trackNo = int(metadata.get('trackno'))
                        except ValueError:
                           trackNo = int(metadata.get('trackno').split('/')[0])
                     else:
                        trackNo = 0

                     if metadata.get('title') is not None:
                        title = to_utf8(metadata.get('title'))
                     else:
                        title = ''

                     if metadata.get('genre') is not None:
                        genre = getGenre(metadata.get('genre'))
                     else:
                        genre = ''

                     # check if it is already in the database
                     if Songs.selectBy(localpath=filename).count() == 0:

                        # it was not in the DB, create a newentry
                        if dbAlbum is not None and dbArtist is not None:
                           song = Songs(
                                 trackNo = trackNo,
                                 title   = title,
                                 localpath = filename,
                                 artist  = dbArtist,
                                 album   = dbAlbum,
                                 genre   = genre,
                                 bitrate = bitrate,
                                 duration = duration,
                                 lastScanned = datetime.datetime.now(),
                                 filesize = filesize
                                 )
                           # we call this after creating the object, as this
                           # prevents the hash being calculated if an error
                           # occurred on song-creation
                           song.checksum = get_hash(filename)
                           scancount += 1

                           self.__scanLog.info("Scanned %s" % ( filename ))
                     else:

                        # we found the song in the DB. Load it so we can update it's
                        # metadata. If it has changed since it was added to the DB!
                        song = Songs.selectBy(localpath=filename)[0]

                        if dbAlbum is not None and dbArtist is not None:
                           if song.lastScanned is None \
                                 or datetime.datetime.fromtimestamp(os.stat(filename).st_ctime) > song.lastScanned:
                              song.localpath = filename
                              song.trackNo = trackNo
                              song.title   = title
                              song.artist  = dbArtist
                              song.album   = dbAlbum
                              song.bitrate = bitrate
                              song.filesize= filesize
                              song.duration = duration
                              song.checksum = get_hash(filename)
                              song.genre    = genre
                              song.lastScanned = datetime.datetime.now()
                              self.__scanLog.info("Updated %s" % ( filename))
                           scancount += 1

                     try:
                        if song.title is not None \
                              and song.artist is not None \
                              and song.album is not None \
                              and song.trackNo != 0:
                           song.isDirty = False
                     except:
                        song.isDirty = True


                  except ValueError, ex:
                     import traceback
                     self.__scanLog.critical("Unexpected error:\n%s" % traceback.format_exc())
                     self.__scanLog.warning("unknown metadata for %s (%s)" % (filename, str(ex)))
                     errorCount += 1
                  except OperationalError, ex:
                     #self.__scanLog.error("%s %s" % (filename, str(ex)))
                     errorCount += 1
                     pass

         self.__scanLog.info("--- done scanning (%7d songs scanned, %7d errors)" % (scancount, errorCount))

      def run(self):
         for folder in self.__folders:
            self.__crawl_directory(folder)

         for song in list(Songs.select()):
            if not os.path.exists(song.localpath):
               self.__scanLog.warning('File %s not found on filesystem.' % song.localpath)
               try:
                  targetSongs = list(Songs.selectBy(
                        title=song.title,
                        artist=song.artist,
                        album=song.album,
                        trackNo=song.trackNo
                        ))

                  for targetSong in targetSongs:
                     if song.localpath != targetSong.localpath:
                        self.__scanLog.info('Song with id %d moved to id %d' % (song.id, targetSong.id))
                        newPath = targetSong.localpath
                        targetSong.destroySelf()
                        song.localpath = newPath
               except IndexError:
                  # no such song found. We can delete the entry from the database
                  self.__scanLog.warning('File %s disappeared!' % song.localpath)
                  song.isDirty = True

         self.__scanLog.info('Done checking filesystem')
         self.__scanLog.info('Checking for empty genres...')
         for x in list(Genres.select()):
            if len(x.songs) == 0:
               self.__scanLog.info('Genre %-15s was empty' % x.name)
               x.destroySelf()
         self.__scanLog.info('Done checking genres')

         self.__scanLog.info('Checking for empty albums...')
         try:
            for x in list(Albums.select()):
               if len(x.songs) == 0:
                  self.__scanLog.info('Album %-15s was empty' % x.title)
                  x.destroySelf()
         except UnicodeDecodeError:
            self.__scanLog.error('UnicodeDecodeError when selecting albums')
         self.__scanLog.info('Done checking albums')

         self.__scanLog.info('--- All done! ---')

   def __init__(self):
      """
      Constructor
      """
      threading.Thread.__init__(self)
      self.setName( '%s (%s)' % (self.getName(), 'Lib') )

   def run(self):
      """
      The control loop for the librarian.
      For now it does not much more than sitting there and wait. Ook!
      """
      self.__logger.info('Started Librarian')
      cycle = int(getSetting('librarian_cycle', '1'))
      while self.__keepRunning:
         # check for active scans
         if len(self.__activeScans) > 0:
            for scan in self.__activeScans:
               if not scan.isAlive():
                  self.__activeScans.remove(scan)
            self.__logger.debug("%s active scans" % len(self.__activeScans))
         time.sleep(cycle)
      if len(self.__activeScans) > 0:
         self.__logger.info('Stopped scans')
         for scan in self.__activeScans:
            #TODO# This does not work as expected
            scan.join(0.0)
      self.__logger.info('Stopped Librarian')

   def stop(self):
      """
      Requests that the librarian should end it's execution and exit
      """
      self.__keepRunning = False

   def rescan(self):
      """
      Spawns a slave thread to rescan the library for each filder specified in
      the settings table
      """
      self.__logger.info("scanning %s (loging redirected to log/scanner.log)" % (getSetting('folders').split(',')))
      thr = self.Scanner(getSetting('folders').split(','))
      thr.start()

   def detect_moves(self):
      """
      Detects files that moved on the file system and updates the reference in
      the DB
      """

      ## wait for scanners to finish their job
      #for item in self.__activeScans:
      #   if item.isAlive():
      #      item.join()
      self.__logger.debug("detecting moves")

   def detect_orphans(self):
      """
      Detects files that do not exist anymore on the file system and marks them
      as orphaned in the database
      """
      self.__logger.debug("detecting orphans")
      pass

   def find_duplicates(self):
      """
      Detects duplicate entries.
      """
      self.__logger.debug("searching for duplicates")
      pass

   def add_file(self, filename):
      """
      Adds a new file to the library
      """
      self.__logger.debug("adding file %s" % (filename))
      pass

   def read_metadata(self, filename):
      """
      Reads the metadata of a file and stores the info
      """
      self.__logger.debug("reading metadata from %s" % (filename))
      pass

   def find_cover_art(self, artist, album):
      """
      Tries to locate the cover art of an album on the net and copies it into
      the album's directory
      """
      self.__logger.debug("finding cover art for %s %s" % (artist, album))
      pass

   def mark_dirty(self, songID):
      """
      Flags a song as dirty, meaning that the metadata is incomplete
      """
      self.__logger.info("marking %s as dirty" % (songID))
      try:
         Songs.get(int(songID)).dirty = True
         return (True, 'OK')
      except Exception, ex:
         return (False, str(ex))

class Arbitrator(threading.Thread):

   """
   Each remote connection get's its own arbitrator that routes user requests to
   the appropriate worker-threads. This simplifies client interaction greatly
   as the complicated stuff all happens under the hood
   """

   global lib        # a reference to the librarian
   __keepRunning = True
   __logger      = logging.getLogger('arb')

   def __init__(self, connection, address):
      """
      Constructor

      PARAMETERS
         connection - A reference to the client connection object
         address    - The address of the connected client
      """
      self.__connection = connection
      self.__address    = address
      threading.Thread.__init__(self)
      self.setName( '%s (%s)' % (self.getName(), 'Arb') )
      self.__logger.debug( "accepted incoming connection from %s" % (address[0]) )

   def dispatch(self, command):
      """
      Routes a command to the appropriate worker thread

      PARAMETERS
         command  - The command received from the client
      """

      try:
         #
         # Library commands
         #
         if command == 'rescanlib':
            lib.rescan()
            lib.detect_moves()    # after importing, we can detect moves
            lib.detect_orphans()  # everything in the db that has no file on HD
                                  # and did not move is orphanded and should be
                                  # removed from the DB
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
         # Juggler commands
         #
         elif command == 'play':
            res = juggler.startPlayback()
            if res[0]: return 'OK:%s\n' % res[1]
            else: return 'ER:%s\n' % res[1]
         elif command == 'pause':
            res = juggler.pausePlayback()
            if res[0]: return 'OK:%s\n' % res[1]
            else: return 'ER:%s\n' % res[1]
         elif command == 'stop':
            res = juggler.stopPlayback()
            if res[0]: return 'OK:%s\n' % res[1]
            else: return 'ER:%s\n' % res[1]
         elif command == 'skip':
            res = juggler.skipSong()
            if res[0]: return 'OK:%s\n' % res[1]
            else: return 'ER:%s\n' % res[1]
         elif command == 'player_status':
            res = juggler.playStatus()
            if res[0]: return 'OK:%s\n' % res[1]
            else: return 'ER:%s\n' % res[1]
         elif command == 'now_playing':
            res = juggler.nowPlaying()
            if res[0]: return 'OK:%s\n' % res[1]
            else: return 'ER:%s\n' % res[1]
         #
         # Unknown commands
         #
         else:
            self.__logger.info("received unknown command: %s" % command)
            return 'ER:UNKNOWN COMMAND\n'
      except Exception, ex:
         import traceback
         self.__logger.critical("Unexpected error:\n%s" % traceback.format_exc())
         return "ER:%s\n" % ex

   def run(self):
      """
      The main control loop of the Arbitrator. It sends a simple "HELLO" to the
      connected client and then starts listening for commands. Before the
      connection ends it sends "BYE"
      """
      self.__logger.debug( "Arbitrator awaiting commands from %s" % self.__address[0] )
      self.__connection.send('HELLO\n')
      try:
         while self.__keepRunning:
            data = self.__connection.recv(1024)[0:-1]
            if data:
               self.__logger.debug( "command from %s: %s" % (self.__address[0], data) )
               self.__connection.send(self.dispatch(data))
            else:
               break
         self.__connection.send('BYE\n')
         self.__connection.close()
      except Exception, ex:
         if str(ex).lower().find('broken pipe') > 0:
            # the client exited, fair enough. let's do the same
            self.__connection.close()
            pass
         else:
            import traceback
            self.__logger.critical("Skipped unexpected error:\n%s" % traceback.format_exc())
      self.__logger.debug( "Arbitrator quit" )

   def stop(self):
      self.__keepRunning = False

class Scrobbler(threading.Thread):

   """
   Submits tracks to last.fm. It does not submit more than one song per minute
   to easen last.fm's load
   """

   __keepRunning = True
   __logger      = logging.getLogger('scro')

   def __init__(self, user, passwd):
      """
      Constructor
      """
      threading.Thread.__init__(self)
      self.setName( '%s (%s)' % (self.getName(), 'Scro') )

      self.__user = user
      self.__pwd  = passwd

   def getConnection(self, user, password):

      url = "post.audioscrobbler.com"

      self.__logger.debug("opening last.fm handshake uri")

      params = urllib.urlencode({
         'hs': 'true',
         'p':  '1.1',
         'c':  'tst',
         'v':  '1.0',
         'u':  user
         })
      conn = httplib.HTTPConnection(url)
      conn.request("GET", "/?%s" % params )
      r = conn.getresponse()
      data = r.read()
      self.__logger.debug("Last.FM response: \n %s" % data)
      conn.close()
      self.__logger.debug("... response received. Authencitating... ")

      challenge = data.split()[1]
      posturl   = data.split()[2]
      interval  = data.split()[4]

      challengeresponse = md5.md5('%s%s' % (password, challenge)).hexdigest()
      return (challengeresponse, posturl, float(interval))

   def scrobble(self, song, time_played):
      pltime = time_played.isoformat(' ')
      if '.' in pltime:
         pltime = pltime.split('.')[0]
      try:
         self.__logger.info('Scrobbling %s - %s' % (song.artist.name, song.title))
         while True:
            try:
               conn = httplib.HTTPConnection(self.__posturl.split('/')[2])
               params = urllib.urlencode({
                  'u': 'exhuma',
                  's': self.__cr,
                  'a[0]': unicode(song.artist.name),
                  't[0]': unicode(song.title),
                  'b[0]': unicode(song.album.title),
                  'm[0]': '',
                  'l[0]': song.duration,
                  'i[0]': pltime
               })
               self.__logger.debug("params: %s" % params)
               headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
               conn.request("POST", '/' + '/'.join(self.__posturl.split('/')[3:]), params, headers)
               r = conn.getresponse()
               data = r.read()
               self.__logger.debug("Last.FM response: \n %s" % data)
               conn.close()
            except Exception, ex:
               # Wait 3 seconds, the loop
               self.__logger.warning('Exception caught (%s). Retrying...' % str(ex))
               time.sleep(3)
               continue
            ## except BadStatusLine:
            ##    # Wait 3 seconds, the loop
            ##    self.__logger.warning('Bad Status Line error received. Retrying...')
            ##    time.sleep(3)
            ##    continue
            # No more exceptions, so we can break out of the loop
            break
      except UnicodeDecodeError:
         import traceback
         logger.critical("UTF-8 error when scrobbling. Skipping this song\n%s" % traceback.format_exc())

   def run(self):
      """
      The main control loop of the Scrobbler.
      It checks once a minute if there are new songs on the scrobbler queue
      that should be submitted, then submits them.
      """

      self.__cr, self.__posturl, self.__interval = self.getConnection(self.__user, self.__pwd)
      self.__logger.debug( "Scrobbler started" )

      while self.__keepRunning:
         try:
            nextScrobble = LastFMQueue.select(orderBy=LastFMQueue.q.id)[0]
            self.scrobble( song = nextScrobble.song, time_played=nextScrobble.time_played )
            nextScrobble.destroySelf()
         except IndexError:
            # nothing to scrobble
            pass
         time.sleep(5)
      self.__logger.debug( "Scrobbler stopped" )

   def stop(self):
      self.__keepRunning = False

# ---- helper functions ------------------------------------------------------
def killAgents():
   """
   Tries to stop all the agents
   """

   if lib is not None: lib.stop(); lib.join()
   if juggler is not None:  juggler.stop();  juggler.join()
   if t is not None:   t.stop();
   if scrobbler is not None: scrobbler.stop()
# ----------------------------------------------------------------------------

if __name__ == "__main__":
   # The main loop of the daemon.

   # set the default encoding for multibyte strings
   kaa.strutils.set_encoding('latin-1')

   # Setting up logging
   if (os.path.exists( 'logging_dev.ini' )):
      print "Using development logging"
      logging.config.fileConfig('logging_dev.ini')
   else:
      logging.config.fileConfig('logging.ini')
   logger = logging.getLogger('daemon')
   logger.info( "===== WJB Deamon starting up ==============" )

   # Retrieve settings from the DB
   host = getSetting('daemon_boundHost', 'localhost')
   port = int(getSetting('daemon_port', '61111'))

   # set up a safety net to kill all the threads in case of an uncaught
   # exception
   juggler  = None # initialise the thread variables
   lib        = None
   t          = None
   scrobbler  = None
   try:
      # Start the librarian
      lib = Librarian(); lib.start()

      # Start the scrobbler
      u = getSetting('lastfm_user', '')
      p = getSetting('lastfm_pass', '')
      if u == '' or p == '' or u is None or p is None:
         logger.info('No lastFM user and password specified. Disabling support...')
      else:
         scrobbler = Scrobbler(u, p); scrobbler.start()

      # start the juggler
      try:
         logger.warning('Overriding channel setting. Getting first channel!')
         juggler= Juggler(Channels.get(1))
      except ValueError, ex:
         if str(ex) == 'unknown player backend':
            logger.error('Unknown player specified in the config')
            killAgents()
            sys.exit(0)
      else:
         juggler.start()

      # Prepare and open up the server-socket
      sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      sock.bind((host, port))
      sock.listen(5)
      logger.info( "listening on %s:%s" % (host, port) )

      # wait for incoming connections until interrupted
      while True:
         try:
            # wait for next client to connect
            connection, address = sock.accept()
            t = Arbitrator(connection, address)
            t.start()
         except KeyboardInterrupt:
            logger.info( "----- Waiting for agents to stop ----------" )
            killAgents()
            logger.info( "===== WJB Deamon shutdown =================" )
            break
         except:
            import traceback
            logger.critical("Uncaught exception!!! Bailing out!\n%s" % traceback.format_exc())
            killAgents()
            logger.info( "===== WJB Deamon shutdown =================" )
            break
   except Exception, ex:
      # The safety net: Stop all threads and print out the stack trace to the
      # log and exit
      killAgents()
      import traceback
      logger.critical("Unexpected error:\n%s" % traceback.format_exc())
      sys.stderr.write('WJB Daemon exited unexpectedly. Check the log for details!')
      killAgents()
      sys.exit(0)

# vim: set ts=3 sw=3 et ai :
