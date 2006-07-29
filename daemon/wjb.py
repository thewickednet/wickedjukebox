#!/usr/bin/python

import threading
import time
import kaa.metadata
import socket, logging, logging.handlers
from model import *
import os, sys
from sqlobject.main import SQLObjectNotFound
from sqlobject.sqlbuilder import *

def getSetting(param_in):
   try:
      return Settings.byParam(param_in).value
   except SQLObjectNotFound, ex:
      words = str(ex).split()
      print
      print "Required parameter %s was not found in the settings table!" % words[6]
      print
      sys.exit(0)

def getArtist(artistName):
   """
   If the artist does not yet exist, create it. Otherwise get the database
   reference.
   """

   if Artists.selectBy(name=artistName).count() == 0:
      return Artists( name = artistName)
   else:
      return Artists.selectBy(name=artistName)[0]

def getGenre(genreName):
   """
   If the genre does not yet exist, create it. Otherwise get the database
   reference.
   """

   if Genres.selectBy(name=genreName).count() == 0:
      return Genres( name = genreName)
   else:
      return Genres.selectBy(name=genreName)[0]

def getAlbum(artistName, albumName):
   """
   If the album does not yet exist, create it. Otherwise get the database
   reference.
   """

   dbArtist = getArtist(artistName)

   if Albums.selectBy(title=albumName).count() == 0:
      album = Albums( title = albumName, added=datetime.datetime.now(), artist=dbArtist )
      return album
   else:
      # check if we have the album with the matching artist
      for album in list(Albums.selectBy(title=albumName)):
         if dbArtist == album.artist:
            return album
      # aha! we have an album with a matching name, but not the artist. that
      # means this is a new album, so we create it
      album = Albums( title = albumName, added=datetime.datetime.now(), artist=dbArtist )
      return album

# ----------------------------------------------------------------------------

class Player:

   def queue(self, filename):
      raise NotImplementedError, "Must override this method"

   def getSong(self):
      raise NotImplementedError, "Must override this method"

class MPD(Player):

   __connection = None

   def __init__(self):
      import mpdclient
      # set up the connection to the daemon
      self.__connection = mpdclient.MpdController(
            host=getSetting('mpd_host'),
            port=int(getSetting('mpd_port'))
            )

   def getPosition(self):
      "Returns the current song position. (currentSec, totalSec)"
      pos = self.__connection.getSongPosition()
      if pos:
         return (pos[0], pos[1])
      else:
         return (0,0)

   def getSong(self):
      return self.__connection.getCurrentSong()

   def playlistPosition(self):
      return self.__connection.status().song

   def queue(self, filename):
      for folder in getSetting('folders').split():
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
      return self.__connection.getStatus().playlistLength

   def cropPlaylist(self, length=10):
      if self.__connection.getStatus().playlistLength > length:
         self.__connection.delete(range(0,
            self.__connection.getStatus().playlistLength - length))

   def skipSong(self):
      self.__connection.next()

   def stopPlayback(self):
      self.__connection.stop()

   def startPlayback(self):
      self.__connection.play()


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

      self.populatePlaylist()

   def __connectMPD(self):
      import mpdclient
      try:
         self.__player = MPD()
      except mpdclient.MpdConnectionPortError, ex:
         try:
            self.__player = None
            logging.error('%s, retry in 5s' % ex)
            time.sleep(5)
            self.__connectMPD()
         except KeyboardInterrupt:
            #todo# This only stops the connection attempt. Application will
            #todo# start up cleanly after that, but without working player
            logging.info('interrupted')
            pass

   def populatePlaylist(self):

      self.__player.cropPlaylist()
      if self.__player.playlistPosition() == self.__player.playlistSize()-1 \
            or self.__player.playlistSize() == 0:
         nextSong = self.__smartGet()
         self.__player.queue(nextSong)

   def run(self):
      logging.info('Started DJ')
      cycle = int(getSetting('dj_cycle'))

      while self.__keepRunning:

         currentPosition = self.__player.getPosition()
         self.populatePlaylist()
         if (currentPosition[1] - currentPosition[0]) == 3:
            try:
               cArtist = Artists.selectBy(name=self.__player.getSong().artist)[0]
               cAlbum  = Albums.selectBy(title=self.__player.getSong().album)[0]
               cTitle  = self.__player.getSong().title
               for song in list(Songs.selectBy(artist=cArtist, title=cTitle)):
                  if cAlbum in song.albums:
                     logging.debug('updating song stats')
                     song.lastPlayed = datetime.datetime.now()
                     song.played = song.played + 1
                     song.syncUpdate()
            except IndexError, ex:
               # no song on the queue. We can ignore this error
               pass

            try:
               # song is soon finished. Add the next one to the playlist
               nextSong = self.__dequeue()
               self.__player.queue(nextSong)
            except IndexError:
               # no song in the queue run smartDj
               nextSong = self.__smartGet()
               self.__player.queue(nextSong)

         time.sleep(cycle)
      logging.info('Stopped DJ')

   def __dequeue(self):
      filename = QueueItem.selectBy(position=1)[0].song.localpath

      # ok, we got the top of the queue. We can now shift the queue
      conn = QueueItem._connection
      posCol = QueueItem.q.position.fieldName
      updatePosition = conn.sqlrepr(
            Update(QueueItem.q,
               {posCol: QueueItem.q.position - 1} ))
      conn.query(updatePosition)
      conn.cache.clear()

      # ok. queue is shifted. now drop all items having a position smaller than
      # -6
      delquery = conn.sqlrepr(Delete(QueueItem.q, where=(QueueItem.q.position < -6)))
      conn.query(delquery)

      return filename


   def __smartGet(self):
      """determine a song that would be best to play next"""

      query = """
         SELECT
            localpath,
            %(playratio)s AS playratio
         FROM songs
         WHERE %(playratio)s IS NULL OR %(playratio)s > 0.3
      """ % {'playratio': "( played / ( played + skipped ) )"}
      import random
      random.seed()
      conn = Songs._connection
      res = conn.queryAll(query)
      out = res[random.randint(0, len(res))][0]
      logging.info("Selected song %s at random. However, this feature is not yet fully implemented" % out)
      return out

   def stop(self):
      self.__keepRunning = False

   def startPlayback(self):
      self.__player.startPlayback()
      return ('OK', 'OK')

   def stopPlayback(self):
      self.__player.stopPlayback()
      return ('OK', 'OK')

   def nextSong(self):
      try:
         cArtist = Artists.selectBy(name=self.__player.getSong().artist)[0]
         cAlbum  = Albums.selectBy(title=self.__player.getSong().album)[0]
         cTitle  = self.__player.getSong().title
         for song in list(Songs.selectBy(artist=cArtist, title=cTitle)):
            if cAlbum in song.albums:
               logging.debug('updating song stats')
               song.skipped = song.skipped + 1
               song.syncUpdate()
      except IndexError, ex:
         # no song on the queue. We can ignore this error
         pass
      self.__player.skipSong()
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

               # check if it is already in the database
               if Songs.selectBy(localpath=os.path.join(root, name)).count() == 0:
                  song = Songs(
                        localpath = os.path.join(root, name),
                        title='',
                        year='',
                        played=0,
                        voted=0,
                        skipped=0,
                        downloaded=0,
                        added=datetime.datetime.now(),
                        lastPlayed=None,
                        bitrate='',
                        filesize=0,
                        checksum='',
                        lyrics='',
                        isDirty=True,
                        artist=None,
                        genre=None
                        )
               else:
                  song = Songs.selectBy(localpath=os.path.join(root, name))[0]

               try:
                  metadata = kaa.metadata.parse(os.path.join(root, name))

                  if metadata.get('artist') is not None:
                     song.artist = getArtist(metadata.get('artist'))

                     if metadata.get('album') is not None:
                        try:
                           dbAlbum = getAlbum(
                                       metadata.get('artist'),
                                       metadata.get('album')
                                    )
                           song.addAlbums(dbAlbum)
                        except Exception, ex:
                           if str(ex).upper().find("DUPLICATE") < 0:
                              # if the word duplicate did not appear we have a
                              # problem
                              raise

                        # we determined an artist _and_ album. So what position
                        # does the track have on that album?
                        if metadata.get('trackno') is not None:
                           song.syncUpdate()
                           conn = AlbumSong._connection
                           trackCol = AlbumSong.q.track.fieldName
                           updateTrack = conn.sqlrepr(
                                 Update(AlbumSong.q,
                                    {trackCol: metadata.get('trackno')},
                                    where=AND(
                                       AlbumSong.q.album_id == dbAlbum.id,
                                       AlbumSong.q.song_id == song.id)))
                           conn.query(updateTrack)
                           conn.cache.clear()

                  if metadata.get('title') is not None:
                     song.title = metadata.get('title')

                  if metadata.get('genre') is not None:
                     song.genre = getGenre(metadata.get('genre'))

                  song.syncUpdate()

               except ValueError:
                  print "unknown metadata for %s" % os.path.join(root, name)
      logging.debug("done scanning")

   def run(self):
      logging.info('Started Librarian')
      cycle = int(getSetting('librarian_cycle'))
      while self.__keepRunning:
         time.sleep(cycle)
      logging.info('Stopped Librarian')

   def stop(self):
      self.__keepRunning = False

   def rescan(self):
      for mediaFolder in getSetting('folders').split():
         threading.Thread(target=self.__crawl_directory, kwargs={'dir': mediaFolder}).start()

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

   logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)-8s %(threadName)-15s %(message)s')
   formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s %(threadName)-15s %(message)s')
   rotfile = logging.handlers.RotatingFileHandler('wjb.log', maxBytes=100*1024, backupCount=3)
   rotfile.setLevel(logging.DEBUG)
   rotfile.setFormatter(formatter)
   logging.getLogger('').addHandler(rotfile)

   host = getSetting('daemon_boundHost')
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

