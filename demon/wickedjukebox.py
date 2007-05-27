import sys, os, threading, mutagen
from model import Setting, create_session, Artist, Album, Song
from datetime import datetime

def wjblog( text ):
   print text

def getSetting(param_in, default=None):
   """
   Retrieves a setting from the database.

   PARAMETERS
      param_in - The name of the setting as string
      default  - (optional) If it's set, it provides the default value in case
                 the value was not found in the database.
   """
   try:
      session = create_session()
      setting = session.query(Setting).selectfirst_by( var=param_in )
      if setting is None:
         # The parameter was not found in the database. Do we have a default?
         if default is not None:
            # yes, we have a default. Return that instead the database value.
            return default
         else:
            print
            print "Required parameter %s was not found in the settings table!" % param_in
            print
            raise
      return setting.value
   except Exception, ex:
      if str(ex).lower().find('connect') > 0:
         logging.critical('Unable to connect to the database. Error was: \n%s' % ex)
         sys.exit(0)
      if str(ex).lower().find('exist') > 0:
         logging.critical('Settings table not found. Did you create the database tables?')
         sys.exit(0)
      else:
         # An unknown error occured. We raise it again
         raise

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

