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
import kaa.metadata
import logging, logging.handlers, logging.config
import socket
from model import *
import os, sys
from sqlobject.main import SQLObjectNotFound
from sqlobject.sqlbuilder import *
from MySQLdb import OperationalError

# ---- Global support functions ----------------------------------------------

def get_hash(filename):
   """
   Return md5 hash.
   https://gumuz.looze.net/svn/gumuz/dupes/dupes.py
   """
   f = open(filename,'rb')
   hsh = md5.new()
   while 1:
      data = f.read(2048)
      if not data: break
      hsh.update(data)
   f.close()
   return hsh.hexdigest()

def killAgents():
   """
   Tries to stop all the agents
   """

   if lib is not None: lib.stop(); lib.join()
   if dj is not None:  dj.stop();  dj.join()
   if t is not None:   t.stop();


def getSetting(param_in, default=None):
   """
   Retrieves a setting from the database.

   PARAMETERS
      param_in - The name of the setting as string
      default  - (optional) If it's set, it provides the default value in case
                 the value was not found in the database.
   """
   try:
      return Settings.byParam(param_in).value
   except SQLObjectNotFound, ex:
      # The parameter was not found in the database. Do we have a default?
      if default is not None:
         # yes, we have a default. Return that instead the database value.
         return default
      else:
         # no, no default specified. This won't work so we tell the user
         words = str(ex).split()
         print
         print "Required parameter %s was not found in the settings table!" % words[6]
         print
         raise
   except Exception, ex:
      if str(ex).lower().find('connect') > 0:
         logging.critical('Unable to connect to the database. Error was: \n%s' % ex)
         killAgents()
         sys.exit(0)
      if str(ex).lower().find('exist') > 0:
         logging.critical('Settings table not found. Did you create the database tables?')
         killAgents()
         sys.exit(0)
      else:
         # An unknown error occured. We raise it again
         raise

def getArtist(artistName):
   """
   If the artist does not yet exist, create it. Otherwise get the database
   reference.

   PARAMETERS
      artistName - The name of the artist to create/retrieve

   RETURNS
      an Artists sql-object
   """

   if artistName is None or artistName == '':
      return None

   if Artists.selectBy(name=artistName).count() == 0:
      return Artists( 
         name = artistName,
         added = datetime.datetime.now()
         )
   else:
      return Artists.selectBy(name=artistName)[0]

def getGenre(genreName):
   """
   If the genre does not yet exist, create it. Otherwise get the database
   reference.

   PARAMETERS
      genreName - The name of the genre to create/retrieve

   RETURNS
      an Genres ssql-object
   """

   if genreName is None or genreName == '':
      return None

   if Genres.selectBy(name=genreName).count() == 0:
      return Genres( name = genreName)
   else:
      return Genres.selectBy(name=genreName)[0]

def getAlbum(artistName, albumName):
   """
   If the album does not yet exist, create it. Otherwise get the database
   reference.

   PARAMETERS
      artistName - The name of the artist of that album
      albumName  - The name of the album to create/retrieve

   RETURNS
      an Albums sql-object
   """

   dbArtist = getArtist(artistName)

   if albumName is None or albumName == '' or dbArtist is None:
      return None

   if Albums.selectBy(title=albumName).count() == 0:
      album = Albums( 
         title = albumName,
         added=datetime.datetime.now(),
         played = 0,
         downloaded = 0,
         type = 'album',
         artist=dbArtist
         )
      return album
   else:
      # check if we have the album with the matching artist
      album = list(Albums.selectBy(title=albumName))[0]
      if dbArtist == album.artist:
         return album
      # aha! we have an album with a matching name, but not the artist. that
      # means this is a "various artist" album, so update it and return it
      album.type='various'
      return album

# ----------------------------------------------------------------------------

class Player:
   """
   An abstract class that each player should inherit.
   """

   def queue(self, filename):
      raise NotImplementedError, "Must override this method"

   def getSong(self):
      raise NotImplementedError, "Must override this method"

class MPD(Player):
   """
   An interface to the music player daemon (mpd).
   mpd is a client-server based audio player. It offers easy bindings to python
   and hence it's a simple implementation
   http://www.musicpd.org
   """

   __connection = None  # The interface to mpd

   def __init__(self):
      """
      Constructor
      Connects to the mpd-daemon.
      """
      import mpdclient
      # set up the connection to the daemon
      self.__connection = mpdclient.MpdController(
            host=getSetting('mpd_host', 'localhost'),
            port=int(getSetting('mpd_port', '6600'))
            )

   def getPosition(self):
      """
      Returns the current position in the song. (currentSec, totalSec)
      """
      pos = self.__connection.getSongPosition()
      if pos:
         return (pos[0], pos[1])
      else:
         return (0,0)

   def getSong(self):
      """
      Returns the currently running song
      """
      return self.__connection.getCurrentSong()

   def playlistPosition(self):
      """
      Returns the position in the playlist as integer
      """
      return self.__connection.status().song

   def queue(self, filename):
      """
      Appends a new song to the playlist, and removes the first entry in the
      playlist if it's becoming too large. This prevents having huge playlists
      after a while playing. 

      PARAMETERS
         filename -  The full path of the file
      """
      for folder in getSetting('folders').split(','):
         # with MPD, filenames are relative to the path specified in the mpd
         # config!! This is handled here.
         if filename.startswith(folder):
            filename = filename[len(folder)+1:]
      logging.info("queuing %s" % filename)
      self.__connection.add([filename])

      # keep the playlist clean
      if self.__connection.getStatus().playlistLength > 10:
         self.__connection.delete([0])

   def playlistSize(self):
      """
      Returns the complete size of the playlist
      """
      return self.__connection.getStatus().playlistLength

   def cropPlaylist(self, length=2):
      """
      Removes items from the *beginning* of the playlist to ensure it has only
      a fixed number of entries.

      PARAMETERS
         length - The new size of the playlist (optional, default=10)
      """
      if self.__connection.getStatus().playlistLength > length:
         self.__connection.delete(range(0,
            self.__connection.getStatus().playlistLength - length))

   def clearPlaylist(self):
      """
      Clears the player's playlist
      """
      self.cropPlaylist(0)

   def skipSong(self):
      """
      Skips the current song
      """
      self.__connection.next()

   def stopPlayback(self):
      """
      Stops playback
      """
      self.__connection.stop()

   def pausePlayback(self):
      """
      Pauses playback
      """
      self.__connection.pause()

   def startPlayback(self):
      """
      Starts playback
      """
      self.__connection.play()

   def status(self):
      """
      Returns the status of the player (play, stop, pause)
      """
      if self.__connection.getStatus().state == 1:
         return 'stop'
      elif self.__connection.getStatus().state == 2:
         return 'play'
      elif self.__connection.getStatus().state == 3:
         return 'pause'
      else:
         return 'unknown (%s)' % self.__connection.getStatus().state

class DJ(threading.Thread):
   """
   The DJ is responsible for music playback. All changes of the playback (play,
   pause, skip, ...) have to be passed to the DJ. The DJ handles updating of
   the play statistics, and continuous playback. It manages the queue from the
   database and automatically adds new songs to the playlist. In case something
   is on the queue it takes off the next item, otherwise it picks a song at
   random.
   """

   __keepRunning   = True  # While this is true, the DJ is alive
   __playStatus    = 'playing'
   __currentSongID = 0
   __logger        = logging.getLogger('dj')

   def __init__(self):
      """
      Constructor

      Connects to the player and prepares the playlist
      """
      threading.Thread.__init__(self)
      self.setName( '%s (%s)' % (self.getName(), 'DJ') )

      # initialise the player
      playerBackend = getSetting('player', 'mpd')
      if playerBackend == 'mpd':
         self.__connectMPD()
      else:
         raise ValueError, 'unknown player backend'

      self.populatePlaylist()

   def __connectMPD(self):
      """
      A helper method to connect to the mpd-player. It will retry until it
      get's a connection.
      """
      import mpdclient
      try:
         self.__player = MPD()
      except mpdclient.MpdConnectionPortError, ex:
         import traceback
         self.__logger.critical("Error connecting to the player:\n%s" % traceback.format_exc())
         killAgents()
         sys.exit(0)

   def populatePlaylist(self):
      """
      First, this ensures the playlist does not grow too large. Then it checks
      if the current song is the last one playing. If that is the case, it will
      add a new song to the playlist.
      """

      self.__player.cropPlaylist()
      if self.__player.playlistPosition() == self.__player.playlistSize()-1 \
            or self.__player.playlistSize() == 0:
         try:
            # song is soon finished. Add the next one to the playlist
            nextSong = self.__dequeue()
            self.__currentSongID = nextSong[0]
            self.__player.queue(nextSong[1])
         except IndexError:
            # no song in the queue run smartDj
            nextSong = self.__smartGet()
            self.__currentSongID = nextSong[0]
            self.__player.queue(nextSong[1])

   def run(self):
      """
      The control loop of the DJ
      Every x seconds (can be customised in the settings) it will check the
      position in the current song. If the song is nearly finished, it will
      take appropriate actions to ensure continuous playback (pick a song from
      the queue, or at random)
      """

      self.__logger.info('Started DJ')
      cycle = int(getSetting('dj_cycle', '1'))

      # while we are alive, do the loop
      while self.__keepRunning:

         # check if the player accidentally went into the "stop" state
         if self.__player.status() == 'stop' and self.__playStatus == 'playing':
            self.__player.clearPlaylist()
            self.populatePlaylist()
            self.__player.startPlayback()

         if self.__player.status() == 'play' and self.__playStatus == 'stopped':
            self.__player.stopPlayback()

         # only queue new songs if we are in play-mode
         if self.__playStatus == 'playing':

            # if the song is soon finished, update stats and pick the next one
            currentPosition = self.__player.getPosition()
            if (currentPosition[1] - currentPosition[0]) == 3 or currentPosition == (0,0):
               if self.__player.getSong():
                  try:

                     # retrieve info from the currently playing song
                     # TODO: This is hardcoded for mpd. It HAS to be abstracted by
                     #       the MPD class.
                     cArtist = Artists.selectBy(name=self.__player.getSong().artist)[0]
                     cAlbum  = Albums.selectBy(title=self.__player.getSong().album)[0]
                     cTitle  = self.__player.getSong().title

                     # I haven't figured out the way to add the album to the select
                     # query. That's why I loop through all songs from a given artist
                     # and title. It's highly unlikely though that there is more than
                     # one entry.
                     song = list(Songs.selectBy(artist=cArtist, title=cTitle, album=cAlbum))[0]
                     song.lastPlayed = datetime.datetime.now()
                     song.played = song.played + 1

                  except IndexError, ex:
                     # no song on the queue. We can ignore this error
                     pass

               self.populatePlaylist()

         # wait for x seconds
         time.sleep(cycle)

      # self.__keepRunning became false. We should quit
      self.__logger.info('Stopped DJ')

   def __dequeue(self):
      """
      Return the filename of the next item on the queue
      """

      nextSong = list(QueueItem.select(orderBy=['added', 'position']))[0]
      filename = nextSong.song.localpath
      songID   = nextSong.id
      nextSong.destroySelf()


      #TODO# The following is based on a wrong assumption of the "position" field.
      # This needs to be discussed!
      ## ok, we got the top of the queue. We can now shift the queue by 1
      ## This is a custom query. This is badly documented by SQLObject. Refer to
      ## the top comment in model.py for a reference
      #conn = QueueItem._connection
      #posCol = QueueItem.q.position.fieldName
      #updatePosition = conn.sqlrepr(
      #      Update(QueueItem.q,
      #         {posCol: QueueItem.q.position - 1} )) # this shifts
      #conn.query(updatePosition)
      #conn.cache.clear()
      #
      ## ok. queue is shifted. now drop all items having a position smaller than
      ## -6
      #delquery = conn.sqlrepr(Delete(QueueItem.q, where=(QueueItem.q.position < -6)))
      #conn.query(delquery)

      return (id, filename)

   def __smartGet(self):
      """
      determine a song that would be best to play next and return it's filename

      TODO The current query completely ignores songs that have only been
           played once and skipped once. A minimum play cound should be
           required before it starts calculating the score.
      """

      query = """
         SELECT
            song_id,
            localpath,
            %(playratio)s AS playratio
         FROM songs
         WHERE %(playratio)s IS NULL OR %(playratio)s > 0.3 OR (played+skipped)<10
      """ % {'playratio': "( played / ( played + skipped ) )"}

      # I won't use ORDER BY RAND() as it is way too dependent on the dbms!
      import random
      random.seed()
      conn = Songs._connection
      res = conn.queryAll(query)
      randindex = random.randint(1, len(res)) -1
      try:
         out = (res[randindex][0], res[randindex][1])
         self.__logger.info("Selected song (%d, %s) at random. However, this feature is not yet fully implemented" % out)
         return out
      except IndexError:
         self.__logger.error('No song returned from query. Is the database empty?')
         pass

   def stop(self):
      """
      Requests the DJ to cease operation and quit
      """
      self.__keepRunning = False

   def startPlayback(self):
      """
      Sends a "play" command to the player backend
      """
      self.__playStatus = 'playing'
      self.__player.startPlayback()
      return ('OK', 'OK')

   def stopPlayback(self):
      """
      Sends a "stop" command to the player backend
      """
      self.__playStatus = 'stopped'
      self.__player.stopPlayback()
      return ('OK', 'OK')

   def pausePlayback(self):
      """
      Sends a "pause" command to the player backend
      """
      if self.__playStatus == 'paused':
         self.__playStatus = 'playing'
      else:
         self.__playStatus = 'paused'
      self.__player.pausePlayback()
      return ('OK', 'OK')

   def skipSong(self):
      """
      Updates play statistics and sends a "next" command to the player backend
      """
      try:
         cArtist = Artists.selectBy(name=self.__player.getSong().artist)[0]
         cAlbum  = Albums.selectBy(title=self.__player.getSong().album)[0]
         cTitle  = self.__player.getSong().title
         song = list(Songs.selectBy(artist=cArtist, title=cTitle, album=cAlbum))[0]
         song.skipped = song.skipped + 1
      except IndexError, ex:
         # no song on the queue. We can ignore this error
         pass
      self.__player.skipSong()
      return ('OK', 'OK')

   def playStatus(self):
      return ("OK", self.__playStatus)

   def nowPlaying(self):
      return ("OK", self.__currentSongID)

class Librarian(threading.Thread):
   """
   The librarian is a worker thread that manages the music library
   """

   __keepRunning = True  # While this is true, the librarian is alive
   __logger      = logging.getLogger('lib')
   __scanLog     = logging.getLogger('lib.scanner')
   __activeScans = []

   def __init__(self):
      """
      Constructor
      """
      threading.Thread.__init__(self)
      self.setName( '%s (%s)' % (self.getName(), 'Lib') )

   def __crawl_directory(self, dir):
      """
      Scans a directory and all its subfolders for media files and stores their
      metadata into the library (DB)
      """

      self.__logger.info("scanning %s (loging redirected to log/scanner.log)" % (dir))
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

               try:
                  # parse the metadata
                  metadata = kaa.metadata.parse(os.path.join(root, name))

                  # if we have an artist, set the artist field.
                  # then, if we *also* have an album, store the album from this
                  # artist and set the song's metadata accordingly.
                  # Finally, the song needs a track position on that album. So
                  # we set it.
                  dbArtist = None
                  dbAlbum  = None
                  if metadata.get('artist') is not None:
                     dbArtist = getArtist(metadata.get('artist'))

                     if metadata.get('album') is not None:
                        try:
                           dbAlbum = getAlbum(
                                       metadata.get('artist'),
                                       metadata.get('album')
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
                        self.__scanLog.warning('error getting album for %s', os.path.join(root, name))
                  else:
                     self.__scanLog.warning('error getting artist for %s', os.path.join(root, name))

                  if metadata.get('length') is not None:
                     duration = int(metadata.get('length'))
                  else:
                     duration = 0

                  filesize = os.stat(os.path.join(root,name)).st_size

                  if metadata.get('bitrate') is not None:
                     bitrate = int(metadata.get('bitrate'))
                  else:
                     bitrate = 0

                  if metadata.get('trackno') is not None:
                     trackNo = int(metadata.get('trackno'))
                  else:
                     trackNo = 0

                  if metadata.get('title') is not None:
                     title = metadata.get('title')
                  else:
                     title = ''

                  # check if it is already in the database
                  if Songs.selectBy(localpath=os.path.join(root, name)).count() == 0:

                     # it was not in the DB, create a skeleton entry
                     song = Songs(
                           trackNo = trackNo,
                           title   = title,
                           localpath = os.path.join(root, name),
                           artist  = dbArtist,
                           album   = dbAlbum,
                           genre   = getGenre(metadata.get('genre')),
                           bitrate = bitrate,
                           duration = duration,
                           checksum = get_hash(os.path.join(root,name)),
                           filesize = filesize
                           )
                     scancount += 1

                     self.__scanLog.info("Scanned %s (%s - %s - %2d - %t %s)" % (
                           os.path.join(root, name),
                           song.artist,
                           song.album,
                           trackNo,
                           title,
                           song.genre
                        ))
                  else:

                     # we found the song in the DB. Load it so we can update it's
                     # metadata. If it has changed since it was added to the DB!
                     song = Songs.selectBy(localpath=os.path.join(root, name))[0]

                     if datetime.datetime.fromtimestamp(os.stat(os.path.join(root,name)).st_mtime) > song.added:
                        song.trackNo = trackNo
                        song.title   = title
                        song.artist  = dbArtist
                        song.album   = dbAlbum
                        song.bitrate = bitrate
                        song.filesize= filesize
                        song.duration = duration
                        song.checksum = get_hash(os.path.join(root,name))
                        song.genre    = getGenre(metadata.get('genre'))
                     scancount += 1

                     self.__scanLog.info("Scanned %s (%s - %s - %2d - %t %s)" % (
                           os.path.join(root, name),
                           song.artist,
                           song.album,
                           trackNo,
                           title,
                           song.genre
                        ))

               except ValueError:
                  self.__scanLog.warning("unknown metadata for %s" % os.path.join(root, name))
                  errorCount += 1
               except OperationalError, ex:
                  self.__scanLog.error("%s %s" % (os.path.join(root, name), str(ex)))
                  errorCount += 1
                  pass

      self.__scanLog.info("--- done scanning (%7d songs scanned, %7d errors)" % (scancount, errorCount))
      self.__logger.info("--- done scanning (%7d songs scanned, %7d errors)" % (scancount, errorCount))

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
      for mediaFolder in getSetting('folders').split(','):
         self.__activeScans.append(
               threading.Thread(
                  target=self.__crawl_directory,
                  kwargs={'dir': mediaFolder})
               )
         self.__activeScans[-1].start()

   def detect_moves(self):
      """
      Detects files that moved on the file system and updates the reference in
      the DB
      """
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
            res = dj.skipSong()
            if res[0]: return 'OK:%s\n' % res[1]
            else: return 'ER:%s\n' % res[1]
         elif command == 'player_status':
            res = dj.playStatus()
            if res[0]: return 'OK:%s\n' % res[1]
            else: return 'ER:%s\n' % res[1]
         elif command == 'now_playing':
            res = dj.nowPlaying()
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
               self.__logger.info( "command from %s: %s" % (self.__address[0], data) )
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
            self.__logger.critical("Unexpected error:\n%s" % traceback.format_exc())
      self.__logger.debug( "Arbitrator quit" )

   def stop(self):
      self.__keepRunning = False

if __name__ == "__main__":
   # The main loop of the daemon.

   # Setting up logging
   logging.config.fileConfig('logging.ini')
   logger = logging.getLogger('daemon')
   logger.info( "===== WJB Deamon starting up ==============" )

   # Retrieve settings from the DB
   host = getSetting('daemon_boundHost', 'localhost')
   port = int(getSetting('daemon_port', '61111'))

   # set up a safety net to kill all the threads in case of an uncaught
   # exception
   dj  = None # initialise the thread variables
   lib = None
   t   = None
   try:
      # Start the librarian
      lib = Librarian(); lib.start()

      # start the DJ
      dj = None
      try:
         dj = DJ()
      except ValueError, ex:
         if str(ex) == 'unknown player backend':
            logger.error('Unknown player specified in the config')
            killAgents()
            sys.exit(0)
      else:
         dj.start()

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
            logger.info( "accepting incoming connection from %s" % (address[0]) )
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
