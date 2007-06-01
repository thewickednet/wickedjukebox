import sys, os, threading, mutagen, time
from model import create_session, Artist, Album, Song, Channel as dbChannel, getSetting
from datetime import datetime
from util import Scrobbler
import player

def wjblog( text ):
   print text

class Librarian(object):

   __activeScans = []

   class Scanner(threading.Thread):

      def __init__(self, folders):
         self.__folders = folders
         threading.Thread.__init__(self)

      def getAlbum( self, meta ):
         if meta.has_key( 'TALB' ):
            return meta.get( 'TALB' ).text[0]
         elif meta.has_key( 'album' ):
            return meta.get('album')[0]
         return None

      def getArtist( self, meta ):
         if meta.has_key( 'TPE1' ):
            return meta.get( 'TPE1' ).text[0]
         elif meta.has_key( 'artist' ):
            return meta.get('artist')[0]
         return None

      def getTitle( self, meta ):
         if meta.has_key( 'TIT2' ):
            return meta.get( 'TIT2' ).text[0]
         elif meta.has_key( 'title' ):
            return meta.get('title')[0]
         # TDRC - year
         # musicbrainz_albumartist
         # title
         return None

      def getGenre( self, meta ):
         if meta.has_key( 'TCON' ):
            return meta.get( 'TCON' ).text[0]
         return None

      def getTrack(self, meta):
         if meta.has_key('TRCK'):
            return meta.get('TRCK').text[0].split('/')[0]
         else:
            if type(meta.get('tracknumber')) == type([]):
               return meta.get('tracknumber')[0].split('/')[0]
            else:
               return meta.get('tracknumber').split('/')[0]
         return None

      def getDuration( self, meta ):
         if meta.info.length is None: return 0
         else: return meta.info.length

      def getBitrate(self, meta ):
         try:
            return meta.info.bitrate
         except AttributeError, ex:
            print "ERROR:", str(ex)
            return None

      def __crawl_directory(self, dir):
         """
         Scans a directory and all its subfolders for media files and stores their
         metadata into the library (DB)
         """

         wjblog( "-------- scanning %s ---------" % (dir) )

         # Only scan the files specified in the settings table
         recognizedTypes = getSetting('recognizedTypes', 'mp3 ogg flac').split()

         # walk through the directories
         scancount  = 0
         errorCount = 0
         session  = create_session()
         for root, dirs, files in os.walk(dir):
            for name in files:
               if type(name) != type( u'' ):
                  name = name.decode(sys.getfilesystemencoding())
               if name.split('.')[-1] in recognizedTypes:
                  # we have a valid file
                  filename = os.path.join(root,name)
                  wjblog( "Scanning %s" % repr(filename) )
                  metadata = mutagen.File( filename )
                  title  = self.getTitle(metadata)
                  album  = self.getAlbum(metadata)
                  artist = self.getArtist(metadata)
                  assert( title is not None,
                        "Title cannot be empty! (file: %s)" % filename )
                  assert( artist is not None,
                        "Artist cannot be empty! (file: %s)" % filename )

                  dbArtist = session.query(Artist).selectfirst_by( name=artist )
                  if dbArtist is None:
                     dbArtist = Artist( name=artist )
                     session.save(dbArtist)
                     session.flush()

                  dbAlbum = session.query(Album).selectfirst_by( name=album )
                  if dbAlbum is None:
                     dbAlbum = Album( name=album, artist=dbArtist )
                     session.save(dbAlbum)
                     session.flush()

                  duration = self.getDuration( metadata )
                  filesize = os.stat(filename).st_size
                  bitrate  = self.getBitrate( metadata )

                  trackNo  = self.getTrack( metadata )
                  title    = self.getTitle( metadata )
                  genre    = self.getGenre( metadata )

                  # check if it is already in the database
                  if session.query(Song).selectfirst_by( localpath=filename ) is None:

                     # it was not in the DB, create a newentry
                     song = Song( localpath = filename, artist=dbArtist, album=dbAlbum )
                     song.trackNo = trackNo
                     song.title   = title
                     song.bitrate = bitrate
                     song.duration = duration
                     song.lastScanned = datetime.now()
                     song.filesize = filesize
                     session.save(song)
                     scancount += 1
                     wjblog( "Scanned %s" % ( repr(filename) ) )

                  else:
                     # we found the song in the DB. Load it so we can update it's
                     # metadata. If it has changed since it was added to the DB!
                     song = session.query(Song).selectfirst_by( localpath=filename )
                     if song.lastScanned is None \
                           or datetime.fromtimestamp(os.stat(filename).st_ctime) > song.lastScanned:

                        song.localpath   = filename
                        song.trackNo     = trackNo
                        song.title       = title
                        song.artist_id   = dbArtist.id
                        song.album_id    = dbAlbum.id
                        song.bitrate     = bitrate
                        song.filesize    = filesize
                        song.duration    = duration
                        song.checksum    = get_hash(filename)
                        ##song.genre       = genre
                        song.lastScanned = datetime.now()
                        session.save(song)
                        wjblog( "Updated %s" % ( filename ) )
                        scancount += 1

                  try:
                     if song.title is not None \
                           and song.artist is not None \
                           and song.album is not None \
                           and song.trackNo != 0:
                        song.isDirty = False
                  except:
                     song.isDirty = True

            session.flush()

         wjblog( "--- done scanning (%7d songs scanned, %7d errors)" % (scancount, errorCount) )

      def run(self):
         for folder in self.__folders:
            self.__crawl_directory(folder)

         ##for song in list(Songs.select()):
         ##   if not os.path.exists(song.localpath):
         ##      self.__scanLog.warning('File %s not found on filesystem.' % song.localpath)
         ##      try:
         ##         targetSongs = list(Songs.selectBy(
         ##               title=song.title,
         ##               artist=song.artist,
         ##               album=song.album,
         ##               trackNo=song.trackNo
         ##               ))

         ##         for targetSong in targetSongs:
         ##            if song.localpath != targetSong.localpath:
         ##               self.__scanLog.info('Song with id %d moved to id %d' % (song.id, targetSong.id))
         ##               newPath = targetSong.localpath
         ##               targetSong.destroySelf()
         ##               song.localpath = newPath
         ##      except IndexError:
         ##         # no such song found. We can delete the entry from the database
         ##         self.__scanLog.warning('File %s disappeared!' % song.localpath)
         ##         song.isDirty = True
         ##for x in list(Genres.select()):
         ##   if len(x.songs) == 0:
         ##      self.__scanLog.info('Genre %-15s was empty' % x.name)
         ##      x.destroySelf()

         ##try:
         ##   for x in list(Albums.select()):
         ##      if len(x.songs) == 0:
         ##         self.__scanLog.info('Album %-15s was empty' % x.title)
         ##         x.destroySelf()
         ##except UnicodeDecodeError:
         ##   self.__scanLog.error('UnicodeDecodeError when selecting albums')

   def __init__(self):
      pass

   def rescanLib(self):
      self.__activeScans.append( self.Scanner( getSetting('mediadir').split(' ') ) )
      self.__activeScans[-1].start()

class Channel(threading.Thread):

   __dbModel   = None
   __scrobbler = None
   sess        = None
   name        = None
   keepRunning = True

   def __init__(self, name):
      self.sess = create_session()
      self.__dbModel = self.sess.query(dbChannel).selectfirst_by( dbChannel.c.name == name )
      if self.__dbModel is not None:
         self.name = self.__dbModel.name
         print "Loaded channel %s" % self.__dbModel

      u = getSetting('lastfm_user', '', self.__dbModel.id)
      p = getSetting('lastfm_pass', '', self.__dbModel.id)
      if u == '' or p == '' or u is None or p is None:
         print 'No lastFM user and password specified. Disabling support...'
      else:
         self.__scrobbler = Scrobbler(u, p); scrobbler.start()

      # setup song scoring coefficients
      self.__neverPlayed = int(getSetting('scoring_neverPlayed', 10))
      self.__playRatio   = int(getSetting('scoring_ratio',        4))
      self.__lastPlayed  = int(getSetting('scoring_lastPlayed',   7))
      self.__songAge     = int(getSetting('scoring_songAge',      0))

      # initialise the player
      self.__player  = player.createPlayer(self.__dbModel.backend,
                                           self.__dbModel.backend_params)
      threading.Thread.__init__(self)

   def __dequeue(self):
      """
      Return the filename of the next item on the queue. If the queue is empty,
      pick one from the prediction queue
      """

      try:
         nextSong = self.sess.query(QueueItem).select(order_by=['added', 'position'], limit=1, offset=0)[0]
         filename = nextSong.song.localpath
         songID   = nextSong.song.id
         self.sess.delete(nextSong)
         self.sess.flush()
      except IndexError:
         # no item on the main queue. Use the internal prediction queue
         if len(self.__predictionQueue) == 0:
            self.__smartGet()
         nextSong = self.sess.query(Song).get( self.__predictionQueue.pop(0)[0] )
         filename = nextSong.localpath
         songID   = nextSong.id


      #TODO# The following is based on a wrong assumption of the "position" field.
      ## This needs to be discussed!
      ## ok, we got the top of the queue. We can now shift the queue by 1
      #      UPDATE QueueItem SET position = position - 1
      ## ok. queue is shifted. now drop all items having a position smaller than
      ## -6
      #      DELETE FROM QueueItem WHERE position < -6

      self.__player.queue(filename)

      return (songID, filename)

   def isStopped(self):
      return self._Thread__stopped

   def stop(self):
      print "Syncronising channel"
      self.sess.save( self.__dbModel )
      self.sess.flush()
      print "Stopping channel"
      if self._Thread__started:
         self.keepRunning = False

   def setBackend(self, backend):
      raise

   def setPlaymode(self, playmode):
      raise

   def run(self):
      while self.keepRunning:
         time.sleep(1)
         print "1"
      print "Channel stopped"

