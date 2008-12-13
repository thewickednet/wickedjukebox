from sqlalchemy import *
import logging
from util import config
from datetime import datetime
from twisted.python import log
from mutagen import File as MediaFile
from os import stat

logger = logging.getLogger(__name__)

if config['database.type'] == 'sqlite':
   import os
   if os.path.exists( config['database.file'] ):
      log.msg("SQLite database found. All good!")
   else:
      import sys
      log.err("SQLite database (as specified in config.ini) does not exist.\
      Please create it based on the SQL script found in data/database.sql")
      sys.exit(0)
   dburi = "%s:///%s" % (
         config['database.type'],
         config['database.file'],
         )
else:
   dburi = "%s://%s:%s@%s/%s" % (
         config['database.type'],
         config['database.user'],
         config['database.pass'],
         config['database.host'],
         config['database.base'],
         )

# MySQL unicode fix
#if config['database.type'] == 'mysql': dburi = dburi + "?use_unicode=1"

def getSetting(param_in, default=None, channel=None, user=None):
   """
   Retrieves a setting from the database.

   @type  param_in: str
   @param param_in: The name of the setting as string
   @param default:  If it's set, it provides the default value in case the
                    value was not found in the database.
   @type  channel:  int
   @param channel:  The channel id if the setting is bound to a channel.
   @type  user:     int
   @param user:     The user id if the setting is bound to a user.
   """

   if int(config['core.debug']) > 0:
      log.msg("Retriveing setting %r for user %r and channel %r (default: %r)..." % (param_in, user, channel, default))

   output = default

   try:
      session = create_session()

      channel_expression = settingTable.c.channel_id == 0
      user_expression = settingTable.c.user_id == 0

      if channel is not None:
         channel_expression = settingTable.c.channel_id == channel

      if user is not None:
         user_expression = settingTable.c.user_id == user

      setting = session.query(Setting).selectfirst_by( and_(Setting.c.var==param_in, channel_expression, user_expression) )

      # if a channel-setting was requested but no entry was found, we fall back to a global setting
      if channel is not None and setting is None:
         if int(config['core.debug']) > 0:
            log.msg("   No per-channel setting found. falling back to global setting...")
         return getSetting( param_in=param_in, default=default, channel=None, user=user )

      if setting is None:
         # The parameter was not found in the database. Do we have a default?
         if default is not None:
            # yes, we have a default. Return that instead the database value.
            if int(config['core.debug']) > 0:
               log.msg("   Requested setting was not found! Returning default value...")
            output = default
         else:
            log.msg( "   Required parameter %s was not found in the settings table!" % param_in )
            output = None
      else:
         output = setting.value

      if int(config['core.debug']) > 0:
         log.msg("   ... returning %r" % output)
         return output

   except Exception, ex:
      if str(ex).lower().find('connect') > 0:
         logger.critical('Unable to connect to the database. Error was: \n%s' % ex)
         sys.exit(0)
      if str(ex).lower().find('exist') > 0:
         logger.critical('Settings table not found. Did you create the database tables?')
         sys.exit(0)
      else:
         # An unknown error occured. We raise it again
         raise

def setState(statename, value):

      sess = create_session()

      # update state in database
      state = sess.query(State).selectfirst_by(state=statename)
      if state is None:
         state = State()
      state.state = statename
      state.value = value
      sess.save(state)
      sess.flush()

# ----------------------------------------------------------------------------
# Table definitions
# ----------------------------------------------------------------------------

metadata = BoundMetaData(dburi, encoding='utf-8', echo=True)
if int(config['core.debug_sql']) > 0:
   log.msg( "Echoing database queries" )
   metadata.engine.echo = True
else:
   metadata.engine.echo = False

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

# ----------------------------------------------------------------------------
# Mappers
# ----------------------------------------------------------------------------

class Genre(object):
   def __init__(self, name):
      self.name = name
      self.added = datetime.now()
   def __repr__(self):
      return "<Genre %s name=%s>" % (self.id, repr(self.name))

class Setting(object):
   pass

class Channel(object):
   def __repr__(self):
      return "<Channel %s name=%s>" % (self.id, repr(self.name))

class Artist(object):

   def __init__( self, name ):
      self.name  = name
      self.added = datetime.now()

   def __repr__(self):
      return "<Artist %s name=%s>" % (self.id, repr(self.name))

class Album(object):

   def __init__( self, name, artist=None, artist_id=None ):
      self.name  = name
      if artist: self.artist_id = artist.id
      elif artist_id: self.artist_id = artist_id
      self.added = datetime.now()

   def __repr__(self):
      return "<Album %s name=%s>" % (self.id, repr(self.name))

class Song(object):
   def __init__( self, localpath, artist, album ):
      if localpath: self.localpath = localpath
      if artist:    self.artist_id = artist.id
      if album:     self.album_id  = album.id
      self.added = datetime.now()

   def __repr__(self):
      return "<Song id=%r artist_id=%r title=%r path=%r>" % (self.id, self.artist_id, self.title, self.localpath)

   def scan_from_file(self, localpath, encoding):
      """
      Scans a file on the disk and loads the metadata from that file

      @param localpath: The absolute path to the file
      @param encoding: The file system encoding
      """

      metadata = None
      try:
         metadata = MediaFile( localpath.encode(encoding) )
      except Exception, ex:
         logger.warning("%r contained invalid metadata. Error message: %r" % (localpath, str(ex) ) )
      self.__artistName    = self.parseArtist( metadata )
      self.__genreName     = self.parseGenre( metadata )
      self.__albumName     = self.parseAlbum( metadata )
      self.localpath = localpath
      self.title     = self.parseTitle( metadata )
      self.duration  = self.parseDuration( metadata )
      self.bitrate   = self.parseBitrate( metadata )
      self.track_no  = self.parseTrack( metadata )
      self.lastScanned = datetime.now()

      try:
         self.filesize = stat(localpath.encode(encoding)).st_size
      except Exception, ex:
         logger.warning(ex)
         self.filesize = None

      self.artist_id = self.get_artist_id( self.__artistName )
      self.genre_id  = self.get_genre_id( self.__genreName )
      self.album_id  = self.get_album_id(self.artist_id, self.__albumName)

   def get_genre_id( self, genre_name ):
      """
      If the genre already exists, return the ID of that genre, otherwise create a new instance

      @param genre_name: The name of the genre
      @return: The ID of the matching genre
      @todo: instead of using the mapped object "Genre" we could use the genre_table for performance gains
      """
      session = create_session()
      genre = session.query(Genre).selectfirst_by( name=genre_name )
      if not genre:
         genre = Genre( name=genre_name )
         session.save(genre)
         session.flush()

      return genre.id

   def get_artist_id( self, artist_name ):
      """
      If the artist already exists, return the ID of that artist, otherwise create a new instance

      @param artist_name: The name of the artist
      @return: The ID of the matching artist
      @todo: instead of using the mapped object "Artist" we could use the artist_table for performance gains
      """
      session = create_session()
      artist = session.query(Artist).selectfirst_by( name=artist_name )
      if not artist:
         artist = Artist( name=artist_name )
         session.save(artist)
         session.flush()

      return artist.id

   def get_album_id( self, artist_id, album_name ):
      """
      If the album already exists, return the ID of that album, otherwise create a new instance

      @param artist_id: The ID of an artist
      @param album_name: The name of the album
      @return: The ID of the matching album
      @todo: instead of using the mapped object "Album" we could use the album_table for performance gains
      """

      session = create_session()
      album = session.query(Album).selectfirst_by( and_(
         albumTable.c.artist_id == artist_id,
         albumTable.c.name      == album_name
         ) )
      if not album:
         album = Album( name=album_name, artist_id=artist_id )
         session.save(album)
         session.flush()
      return album.id

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
            logger.warning(ex)
      return "unknown title"

   def parseAlbum( self, meta ):
      "Extracts the album name from the metadata object"
      if meta:
         try:
            if 'TALB' in meta:
               return meta.get( 'TALB' ).text[0]
            elif 'album' in meta:
               return meta.get('album')[0]
         except Exception, ex:
            logger.warning(ex)
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
            logger.warning(ex)
      return "unknown artist"

   def parseGenre( self, meta ):
      "Extracts the genre from the metadata object"
      if meta:
         try:
            if 'TCON' in meta:
               if meta.get( 'TCON' ).text[0] != '':
                  return meta.get( 'TCON' ).text[0]
         except Exception, ex:
            logger.warning(ex)
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
            logger.warning("Error retrieving bitrate: %s", str(ex))
      return None

class QueueItem(object):
   def __init__(self):
      self.added = datetime.now()

   def __repr__(self):
      return "<QueueItem %s>" % (self.id)

class DynamicPlaylist(object):
   def __repr__(self):
      return "<DynamicPlaylist %s>" % (self.id)

class ChannelStat(object):

   def __init__( self, songid, channelid ):
      self.song_id    = songid
      self.channel_id = channelid

   def __repr__(self):
      return "<ShannelStat song_id=%s channel_id=%s>" % (self.song_id, self.channel_id)

class LastFMQueue(object):

   def __init__( self, songid, started ):
      self.song_id = songid
      self.time_started = started
      if getSetting('sys_utctime', 0) == 0:
         self.time_played = datetime.utcnow()
      else:
         self.time_played = datetime.now()

class State(object):
   pass

mapper( State, stateTable, properties={
      ##'channel': relation(Channel)
   })
mapper( Genre, genreTable )
mapper( LastFMQueue, lastfmTable, properties={
      'song': relation(Song)
      } )
mapper( ChannelStat, channelSongs )
mapper( DynamicPlaylist, dynamicPLTable )
mapper(QueueItem, queueTable, properties={
         'song': relation(Song)
      })
mapper(Setting, settingTable)
mapper(Channel, channelTable)
mapper(Album, albumTable, properties=dict(
   songs=relation(Song, backref='album')))

mapper(Artist, artistTable, properties=dict(
   albums= relation(Album, backref='artist'),
   songs = relation(Song,  backref='artist')
   ))
mapper(Song, songTable, properties=dict(
   channelstat=relation( ChannelStat, backref='song' ),
   genres = relation( Genre, secondary=song_has_genre, backref='songs' )
   ))
