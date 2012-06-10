import sys, os, threading, mutagen
sys.path.insert(1, '..')
from model import create_session, Artist, Album, Song, \
                  getSetting,\
                  Genre, genreTable
from sqlalchemy import and_
from datetime import datetime
from util import fs_encoding
from wickedjukebox.demon.util import config
from wickedjukebox.util import direxists
import logging
logger = logging.getLogger(__name__)

def fsdecode( string ):
   try:
      if type(string) == type(u''):
         print "%r is already a unicode object!" % (string)
         return string
      return string.decode( fs_encoding )
   except UnicodeDecodeError:
      import traceback; traceback.print_exc()
      print  "Failed to decode %s using %s" % (`string`, fs_encoding)
      return False

def fsencode( string ):
   try:
      return string.encode( fs_encoding )
   except UnicodeEncodeError:
      import traceback; traceback.print_exc()
      print  "Failed to encode %s using %s" % (`string`, fs_encoding)
      return False

class Scanner(threading.Thread):

      __abort     = False
      __cap       = ''
      __forceScan = False
      __total_files = 0
      __scanned_files = 0
      __callback  = None
      __errors    = []

      def abort(self):
         self.__abort = True

      def __init__(self, folders, args=None):

         if args is not None:
            self.__forceScan = args[0] != '0'
            try:
               self.__cap       = args[1]
            except IndexError:
               # no cap was specified. We can live with that
               import traceback; traceback.print_exc()
               pass

         self.__folders = folders
         self.__errors  = []
         threading.Thread.__init__(self)

      def getAlbum( self, meta ):
         if meta is None: return None
         if meta.has_key( 'TALB' ):
            return meta.get( 'TALB' ).text[0]
         elif meta.has_key( 'album' ):
            return meta.get('album')[0]
         return None

      def getArtist( self, meta ):
         if meta is None: return None
         if meta.has_key( 'TPE1' ):
            return meta.get( 'TPE1' ).text[0]
         elif meta.has_key( 'artist' ):
            return meta.get('artist')[0]
         return None

      def getTitle( self, meta ):
         if meta is None: return None
         if meta.has_key( 'TIT2' ):
            return meta.get( 'TIT2' ).text[0]
         elif meta.has_key( 'title' ):
            return meta.get('title')[0]
         # TDRC - year
         # musicbrainz_albumartist
         # title
         return None

      def getGenre( self, meta ):
         try:
            if meta.has_key( 'TCON' ):
               if meta.get( 'TCON' ).text[0] != '':
                  return meta.get( 'TCON' ).text[0]
         except:
            import traceback; traceback.print_exc()
            pass
         return None

      def getTrack(self, meta):
         if meta is None: return None
         if meta.has_key('TRCK'):
            return meta.get('TRCK').text[0].split('/')[0]
         else:
            if meta.get('tracknumber') is None:
               return None
            if type(meta.get('tracknumber')) == type([]):
               return meta.get('tracknumber')[0].split('/')[0]
            else:
               return meta.get('tracknumber').split('/')[0]
         return None

      def getDuration( self, meta ):
         if meta is None: return None
         if meta.info.length is None: return 0
         else: return meta.info.length

      def getBitrate(self, meta ):
         if meta is None: return None
         if 'audio/x-flac' in meta.mime: return None
         try:
            return meta.info.bitrate
         except AttributeError, ex:
            import traceback; traceback.print_exc()
            logging.error("Internal Error", exc_info=True)
            self.__errors.append("Error retrieving bitrate: %s", str(ex))
            return None

      def __crawl_directory(self, dir, cap='', forceScan=False):
         """
         Scans a directory and all its subfolders for media files and stores their
         metadata into the library (DB)

         @type  dir: str
         @param dir: the root directory from which to start the scan

         @type  cap: str
         $param cap: limit crawling to the subset of <dir> starting with <cap>
                     so when scanning "/foo/bar" with a <cap> of 'ba' will scan::

                        /foo/bar/baz
                        /foo/bar/battery
                        /foo/bar/ba/nished

                     but not::

                        /foo/bar/jane
         """
         if type(cap) != type( u'' ) and cap is not None:
            cap = cap.decode(fs_encoding)

         if not os.path.exists( dir.encode(fs_encoding) ):
            logging.warning( "Folder '%s' not found!" % (dir) )
            return

         logging.info( "-------- scanning %s (cap='%s')---------" % (dir,cap) )

         # Only scan the files specified in the settings table
         recognizedTypes = getSetting('recognizedTypes', 'mp3 ogg flac').split()

         # count files
         logging.info( "-- counting..." )
         self.__total_files = 0
         for root, dirs, files in os.walk(dir.encode(fs_encoding)):

            root = fsdecode(root)
            if root is False: continue

            for name in files:
               if type(name) != type( u'' ):
                  name = fsdecode(name)
                  if name is False: continue
               localname = os.path.join(root,name)[ len(dir)+1: ]
               if name.split('.')[-1] in recognizedTypes and localname.startswith(cap):
                  self.__total_files += 1
               for x in dirs:
                  x = fsdecode(x)
                  if x is False: continue
                  if not x.startswith(cap): dirs.remove(x.encode(fs_encoding))

         # walk through the directories
         self.__scanned_files  = 0

         # TODO - getfilesystemencoding is *not* guaranteed to return the
         # correct encodings on *nix systems as the FS-encodings are not
         # enforced on these systems! It will crash here with a
         # UnicodeDecodeError if an unexpected encoding is found. Instead, it
         # should skip that file and print an print a useful message.
         self.__scanned_files = 0
         for root, dirs, files in os.walk(dir.encode(fs_encoding)):

            # if an abort is requested we exit right away
            if self.__abort is True: break;

            session  = create_session()
            root = fsdecode(root)
            if root is False: continue
            for name in files:
               if type(name) != type( u'' ):
                  name = fsdecode(name)
                  if name is False: continue
               filename = os.path.join(root,name)
               localname = os.path.join(root,name)[ len(dir)+1: ]
               if name.split('.')[-1] in recognizedTypes and localname.startswith(cap):
                  # we have a valid file
                  if config['core.debug'] != "0":
                     try:
                        logging.info( "[%6d/%6d (%03.2f%%)] %s" % (
                           self.__scanned_files,
                           self.__total_files,
                           self.__scanned_files/float(self.__total_files)*100,
                           repr(os.path.basename(filename))
                           ))
                     except ZeroDivisionError:
                        logging.info( "[%6d/%6d (%5s )] %s" % (
                           self.__scanned_files,
                           self.__total_files,
                           '?',
                           repr(os.path.basename(filename))
                           ))
                  elif self.__scanned_files % 1000 == 0:
                     logging.info("Scanned %d out of %d files" % (self.__scanned_files, self.__total_files))

                  try:
                     metadata = mutagen.File( filename.encode(fs_encoding) )
                  except Exception, ex:
                     import traceback; traceback.print_exc()
                     logging.warning( "%r contained no valid metadata! Excetion message: %s" % (filename, str(ex)) )
                     self.__errors.append( str(ex) )
                     continue
                  title  = self.getTitle(metadata)
                  album  = self.getAlbum(metadata)
                  artist = self.getArtist(metadata)
                  if title is None:
                     self.__errors.append( "Title of %r was empty! Not scanned!" % filename )
                     continue

                  if artist is None:
                     self.__errors.append( "Artist of  %r was empty! Not scanned!" % filename )
                     continue

                  dbArtist = session.query(Artist).selectfirst_by( name=artist )
                  if dbArtist is None:
                     dbArtist = Artist( name=artist )
                     session.save(dbArtist)
                     session.flush()

                  dbAlbum = session.query(Album).selectfirst_by( and_(name=album, artist_id=dbAlbum.id) )
                  if dbAlbum is None:
                     dbAlbum = Album( name=album, artist=dbArtist )
                     session.save(dbAlbum)
                     session.flush()

                  duration = self.getDuration( metadata )
                  filesize = os.stat(filename.encode(fs_encoding)).st_size
                  bitrate  = self.getBitrate( metadata )

                  track_no = self.getTrack( metadata )
                  title    = self.getTitle( metadata )
                  genreNm  = self.getGenre( metadata )
                  genre    = None
                  if genreNm is not None:
                     genre    = session.query(Genre).selectfirst_by( genreTable.c.name == genreNm )
                     if genre is None:
                        genre = Genre( name = genreNm )
                        session.save(genre)
                        session.flush()

                  # check if it is already in the database
                  song = session.query(Song).selectfirst_by( localpath=filename )
                  if song is None:

                     # it was not in the DB, create a new entry
                     song = Song( localpath = filename, artist=dbArtist, album=dbAlbum )
                     if genre is not None:
                        song.genres.append( genre )

                  else:
                     # we found the song in the DB. Load it so we can update it's
                     # metadata. If it has changed since it was added to the DB!
                     if forceScan \
                           or song.lastScanned is None \
                           or datetime.fromtimestamp(os.stat(filename.encode(fs_encoding)).st_ctime) > song.lastScanned:

                        song.localpath   = filename
                        song.artist_id   = dbArtist.id
                        song.album_id    = dbAlbum.id
                        if genre is not None and genre not in song.genres:
                           song.genres      = []
                           song.genres.append( genre )
                        if config['core.debug'] != "0":
                           logging.info( "Updated %s" % ( filename ) )

                  song.title       = title
                  song.track_no    = track_no
                  song.bitrate     = bitrate
                  song.duration    = duration
                  song.filesize    = filesize
                  song.lastScanned = datetime.now()
                  self.__scanned_files       += 1

                  try:
                     if song.title is not None \
                           and song.artist is not None \
                           and song.album is not None \
                           and song.track_no != 0:
                        song.isDirty = False
                  except:
                     import traceback; traceback.print_exc()
                     song.isDirty = True

                  session.save(song)

            session.flush()
            session.close()

            # remove subdirectories from list that do not match the capping
            for x in dirs:
               x = fsdecode(x)
               if x is False: continue
               if not x.startswith(cap): dirs.remove(x.encode(fs_encoding))

         logging.info( "--- done scanning (%7d/%7d songs scanned, %7d errors)"
               % (self.__scanned_files, self.__total_files, len(self.__errors))
               )

      def run(self):
         for folder in self.__folders:
            self.__crawl_directory(folder, self.__cap, self.__forceScan)

         session  = create_session()
         session.close()
         if self.__callback is not None:
            self.__callback()

      def get_status(self):
         return {
            "total_files": self.__total_files,
            "scanned_files": self.__scanned_files,
            "errors": self.__errors,
            }

      def add_callback(self, func):
         self.__callback = func

class Librarian(object):

   __activeScans = []

   def __init__(self):
      pass

   def abortAll(self):
      for x in self.__activeScans:
         x.abort()

   def rescanLib(self, args=None):

      mediadirs = [ x for x in getSetting('mediadir').split(' ') if direxists(x) ]

      if mediadirs != []:
         self.__activeScans.append( Scanner( mediadirs, args ) )
         self.__activeScans[-1].start()

