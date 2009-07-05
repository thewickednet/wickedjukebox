from sqlalchemy import create_engine, Table, Column, MetaData, Unicode
from sqlalchemy.sql import select, update, delete, insert
from sqlalchemy.orm import mapper, sessionmaker
from pydata import util
from datetime import datetime
import sys
from mutagen import File as MediaFile
import logging
import logging.config
logging.config.fileConfig("logging.ini")

LOG = logging.getLogger(__name__)
CFG = util.loadConfig( "config.ini" )
DBURI = "%s://%s:%s@%s/%s" % (
         CFG['database.type'],
         CFG['database.user'],
         CFG['database.pass'],
         CFG['database.host'],
         CFG['database.base'],
         )

metadata = MetaData()
engine = create_engine(DBURI, echo=True)
metadata.bind = engine
Session = sessionmaker(bind=engine)

stateTable     = Table( 'state', metadata,
      autoload=True )
channelTable   = Table( 'channel', metadata,
      Column( 'name', Unicode(32) ),
      Column( 'backend', Unicode(64) ),
      Column( 'backend_params', Unicode() ),
      autoload=True )
settingTable   = Table( 'setting', metadata,
      Column( 'value', Unicode()),
      autoload=True )
settingTextTable   = Table( 'setting_text', metadata,
      Column( 'comment', Unicode()),
      autoload=True )
artistTable    = Table( 'artist', metadata,
      Column('name', Unicode(128)),
      autoload=True )
albumTable     = Table( 'album', metadata,
      Column( 'name', Unicode(128) ),
      Column( 'type', Unicode(32) ),
      autoload=True )
songTable      = Table( 'song', metadata,
      Column( 'title', Unicode(128) ),
      Column( 'localpath', Unicode(255) ),
      Column( 'lyrics', Unicode() ),
      autoload=True )
queueTable     = Table( 'queue', metadata, autoload=True )
channelSongs   = Table( 'channel_song_data', metadata, autoload=True )
lastfmTable    = Table( 'lastfm_queue', metadata, autoload=True )
usersTable     = Table( 'users', metadata, autoload=True )
dynamicPLTable = Table( 'dynamicPlaylist', metadata,
      Column( 'label', Unicode(64) ),
      Column( 'query', Unicode() ),
      autoload=True )
song_has_genre = Table( 'song_has_genre', metadata, autoload=True )
genreTable     = Table( 'genre', metadata, autoload=True )
songStandingTable = Table( 'user_song_standing', metadata, autoload=True )

class Setting(object):
   @classmethod
   def get(self, param_in, default=None, channel_id=None, user_id=None):
      """
      Retrieves a setting from the database.

      @type  param_in:   str
      @param param_in:   The name of the setting as string
      @param default:    If it's set, it provides the default value in case the
                         value was not found in the database.
      @type  channel_id: int
      @param channel_id: The channel id if the setting is bound to a channel.
      @type  user_id:    int
      @param user_id:    The user id if the setting is bound to a user.
      """

      LOG.debug("Retriveing setting %r for user %r and channel %r (default: %r)..." % (param_in, user_id, channel_id, default))

      output = default

      try:
         s = select( [settingTable.c.value] )
         s = s.where( settingTable.c.var == param_in )

         if channel_id:
            s = s.where( settingTable.c.channel_id == channel_id )
         else:
            s = s.where( settingTable.c.channel_id == 0 )

         if user_id:
            s = s.where( settingTable.c.user_id == user_id )
         else:
            s = s.where( settingTable.c.user_id == 0 )

         r = s.execute()
         if r:
            setting = r.fetchone()

         # if a channel-setting was requested but no entry was found, we fall back to a global setting
         if channel_id and not setting:
            LOG.debug("   No per-channel setting found. falling back to global setting...")
            return getSetting( param_in=param_in, default=default, channel_id=None, user_id=user_id )

         if not setting:
            # The parameter was not found in the database. Do we have a default?
            if default:
               # yes, we have a default. Return that instead the database value.
               LOG.debug("   Requested setting was not found! Returning default value...")
               output = default
            else:
               LOG.debug( "   Required parameter %s was not found in the settings table!" % param_in )
               output = None
         else:
            output = setting["value"]

         LOG.debug("   ... returning %r" % output)
         return output

      except Exception, ex:
         if str(ex).lower().find('connect') > 0:
            LOG.critical('Unable to connect to the database. Error was: \n%s' % ex)
            sys.exit(0)
         if str(ex).lower().find('exist') > 0:
            LOG.critical('Settings table not found. Did you create the database tables?')
            sys.exit(0)
         else:
            # An unknown error occured. We raise it again
            raise

class State(object):
   @classmethod
   def set(self, statename, value, channel_id=0):
      """
      Saves a state variable into the database

      @param statename: The variable name
      @param value    : The value of the state variable
      @param channel_id: (optional) For channel based states, use this to set
                         the channel.
      """

      s = select( [stateTable.c.state] )
      s = s.where( stateTable.c.state == statename )
      s = s.where( stateTable.c.channel_id == channel_id )
      r = s.execute()
      if r and r.fetchone():
         # the state exists, we need to update it
         uq = update( stateTable )
         uq = uq.values( {'value': value, 'channel_id': channel_id} )
         uq = uq.where( stateTable.c.state == statename )
         uq = uq.where( stateTable.c.channel_id == channel_id )
         uq.execute()
      else:
         # unknown state, store it in the DB
         ins_q = insert( stateTable )
         ins_q = ins_q.values( { 'state': statename, 'value': value, 'channel_id': channel_id } )
         ins_q.execute()

      LOG.debug( "State %r stored with value %r for channel %r" % ( statename, value, channel_id ) )

   @classmethod
   def get(self, statename, channel_id=0):
      """
      Retrieve a specific state

      @param: The variable name
      @param: (optional) The channel id for states bound to a specific channel
      @return: The state value
      """
      s = select( [stateTable.c.value] )
      s = s.where( stateTable.c.state == statename )
      s = s.where( stateTable.c.channel_id == channel_id )
      r = s.execute()
      if r:
         row = r.fetchone()
         if row:
            return row[0]
      LOG.debug( "State %r not found for channel %r" % ( statename, channel_id ) )
      return None

class Album(object):

   def __init__( self, name, artist=None, artist_id=None, path=None ):
      self.name  = name
      if artist: self.artist_id = artist.id
      elif artist_id: self.artist_id = artist_id

      self.path = path
      self.added = datetime.now()

   def __repr__(self):
      return "<Album %s name=%s>" % (self.id, repr(self.name))

class Song(object):

   def __init__( self, localpath, artist, album ):
      if localpath: self.localpath = localpath
     # if artist:    self.artist_id = artist.id
     # if album:     self.album_id  = album.id
      self.added = datetime.now()

   def __repr__(self):
      return "<Song id=%r artist_id=%r title=%r path=%r>" % (self.id, self.artist_id, self.title, self.localpath)

   def scan_from_file(self, localpath, encoding):
      """
      Scans a file on the disk and loads the metadata from that file

      @param localpath: The absolute path to the file
      @param encoding: The file system encoding
      """

      from os import path

      audiometa = None
      LOG.debug( "Extracting metadata from %r" % localpath )

      try:
         audiometa = MediaFile( localpath.encode(encoding) )
      except Exception, ex:
         LOG.warning("%r contained invalid metadata. Error message: %r" % (localpath, str(ex) ) )

      dirname = path.dirname( localpath.encode(encoding) )

      self.__artistName = self.parseArtist( audiometa )
      self.__genreName  = self.parseGenre( audiometa )
      self.__albumName  = self.parseAlbum( audiometa )
      self.localpath    = localpath
      self.title        = self.parseTitle( audiometa )
      self.duration     = self.parseDuration( audiometa )
      self.bitrate      = self.parseBitrate( audiometa )
      self.track_no     = self.parseTrack( audiometa )

      release_date   = self.parseReleaseYear( audiometa )
      if release_date:
         self.year = release_date.year

      try:
         self.filesize = stat(localpath.encode(encoding)).st_size
      except Exception, ex:
         LOG.warning(ex)
         self.filesize = None

      self.artist_id = self.get_artist_id( self.__artistName )
      self.genre_id  = self.get_genre_id( self.__genreName )
      self.album_id  = self.get_album_id(dirname)
      self.lastScanned = datetime.now()

   def get_genre_id( self, genre_name ):
      """
      If the genre already exists, return the ID of that genre, otherwise create a new instance

      @param genre_name: The name of the genre
      @return: The ID of the matching genre
      @todo: instead of using the mapped object "Genre" we could use the genreTable for performance gains
      """

      testsel = select( [genreTable.c.id] )
      testsel = testsel.where( genreTable.c.name == genre_name )
      res = testsel.execute()
      row = res.fetchone()
      if row:
         return row[0]

      insq = insert( genreTable ).values({
            'name': genre_name
         })
      result = insq.execute()
      return result.last_inserted_ids()[0]

   def get_artist_id( self, artist_name ):
      """
      If the artist already exists, return the ID of that artist, otherwise create a new instance

      @param artist_name: The name of the artist
      @return: The ID of the matching artist
      @todo: instead of using the mapped object "Artist" we could use the artistTable for performance gains
      """

      testsel = select( [artistTable.c.id] )
      testsel = testsel.where( artistTable.c.name == artist_name )
      res = testsel.execute()
      row = res.fetchone()

      if row:
         return row[0]

      insq = insert( artistTable ).values({
            'name': artist_name
         })
      result = insq.execute()
      return result.last_inserted_ids()[0]

   def get_album_id( self, dirname ):
      """
      If the album already exists, return the ID of that album, otherwise create a new instance

      @param artist_id: The ID of an artist
      @param album_name: The name of the album
      @param dirname: The path where the files of this album are stored
      @return: The ID of the matching album
      @todo: instead of using the mapped object "Album" we could use the albumTable for performance gains
      """
      if not self.artist_id or not self.__albumName:
         LOG.warning( "Unable to determine the album ID without a valid srtist_id and album-name!" )

      artist_id = self.artist_id
      album_name = self.__albumName

      testsel = select( [albumTable.c.id, albumTable.c.release_date] )
      testsel = testsel.where( albumTable.c.path == dirname )
      row = testsel.execute().fetchone()

      album_id = None
      if row:
         album_id = row[0]

      if not album_id:
         data = {
               'name': album_name,
               'artist_id': artist_id,
               'path': dirname,
            }
         if self.year:
            data["release_date"] = date(self.year, 1, 1)

         insq = insert( albumTable ).values(data)
         result = insq.execute()
         album_id = result.last_inserted_ids()[0]

      # if this song's release date is newer than the album's release date, we update the album release date
      if self.year:
         if (row["release_date"] and row["release_date"] < date(self.year, 1, 1)) \
            or (not album["release_date"] and self.year):

            updq = update( albumTable )
            updq = updq.where( albumTable.c.path == dirname )
            updq = updq.values({ 'release_date': date( self.year, 1, 1 ) })
            updq.execute()

      return album_id

   def parseTitle( self, meta ):
      "Extracts the title from the metadata object"
      if meta:
         try:
            if 'TIT2' in meta:
               return meta.get( 'TIT2' ).text[0]
            elif 'title' in meta:
               return meta.get('title')[0]
            # TDRC - year
            # musicbrainz_albumartist
            # title
         except Exception, ex:
            LOG.warning(ex)
      return "unknown title"

   def parseReleaseYear( self, meta ):
      "Extracts the release year from the metadata object"
      try:
         record_date = meta.get("TDRC")
         if record_date and record_date.text:
            raw_string = record_date.text[0].text
            if not raw_string:
               return None

            elements = raw_string.split("-")

            if len(elements) == 1:
               return date(int(elements[0]), 1, 1)
            elif len(elements) == 2:
               return date(int(elements[0]), int(elements[1]), 1)
            elif len(elements) == 3:
               return date(int(elements[0]), int(elements[1]), int(elements[2]))

      except Exception, e:
         LOG.error( "Unable to set release year: " + str(e) )

   def parseAlbum( self, meta ):
      "Extracts the album name from the metadata object"
      if meta:
         try:
            if 'TALB' in meta:
               return meta.get( 'TALB' ).text[0]
            elif 'album' in meta:
               return meta.get('album')[0]
         except Exception, ex:
            LOG.warning(ex)
      return "unknown album"

   def parseArtist( self, meta ):
      "Extracts the artist name from the metadata object"
      if meta:
         try:
            if 'TPE1' in meta:
               return meta.get( 'TPE1' ).text[0]
            elif 'artist' in meta:
               return meta.get('artist')[0]
         except Exception, ex:
            LOG.warning(ex)
      return "unknown artist"

   def parseGenre( self, meta ):
      "Extracts the genre from the metadata object"
      if meta:
         try:
            if 'TCON' in meta:
               if meta.get( 'TCON' ).text[0] != '':
                  return meta.get( 'TCON' ).text[0]
         except Exception, ex:
            LOG.warning(ex)
      return "unknown genre"

   def parseTrack(self, meta):
      "Extracts the track number from the metadata object"
      if meta:
         if 'TRCK' in meta:
            return meta.get('TRCK').text[0].split('/')[0]
         else:
            if not meta.get('tracknumber'):
               return None
            if isinstance(meta.get('tracknumber'), list):
               return meta.get('tracknumber')[0].split('/')[0]
            else:
               return meta.get('tracknumber').split('/')[0]
      return None

   def parseDuration( self, meta ):
      "Extracts the track duration from the metadata object"
      if meta and meta.info.length:
         return meta.info.length
      return None

   def parseBitrate(self, meta ):
      "Extracts the bitrate from the metadata object"
      if meta:
         if 'audio/x-flac' in meta.mime: return None
         try:
            return meta.info.bitrate
         except AttributeError, ex:
            LOG.warning("Error retrieving bitrate: %s", str(ex))
      return None

class ChannelStat(object):
   def __init__( self, song_id, channel_id ):
      self.song_id    = song_id
      self.channel_id = channel_id

class Artist(object):
   def __init__( self, name ):
      self.name  = name
      self.added = datetime.now()

class QueueItem(object):
   def __init__(self):
      self.added = datetime.now()

def getSetting(param_in, default=None, channel_id=None, user_id=None):
   import traceback
   tb = traceback.extract_stack()
   source = tb[-2]
   LOG.warning( "DEPRECTAED: Please use Setting.get!\nSource: %s:%d --> %s" % ( source[0], source[1], source[3] ) )
   return Setting.get( param_in, default, channel_id, user_id )

def setState(statename, value, channel_id=0):
   import traceback
   tb = traceback.extract_stack()
   source = tb[-2]
   LOG.warning( "DEPRECTAED: Please use Setting.set!\nSource: %s:%d --> %s" % ( source[0], source[1], source[3] ) )
   return State.set( statename, value, channel_id )

def getState(statename, channel_id=0):
   import traceback
   tb = traceback.extract_stack()
   source = tb[-2]
   LOG.warning( "DEPRECTAED: Please use State.get!\nSource: %s:%d --> %s" % ( source[0], source[1], source[3] ) )
   return State.get( statename, channel_id )

mapper(Song, songTable)
mapper(Album, albumTable)
mapper(ChannelStat, channelSongs )
mapper(Artist, artistTable )
mapper(QueueItem, queueTable )

if __name__ == "__main__":
   print getSetting( "test" )
