from sqlalchemy import *
from util import config
from datetime import datetime
from twisted.python import log

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
if config['database.type'] == 'mysql': dburi = dburi + "?use_unicode=1"

def getSetting(param_in, default=None, channel=None):
   """
   Retrieves a setting from the database.

   @type  param_in: str
   @param param_in: The name of the setting as string
   @param default:  If it's set, it provides the default value in case the
                    value was not found in the database.
   @type  channel:  int
   @param channel:  The channel id if the setting is bound to a channel.
   """
   try:
      session = create_session()
      if channel is None:
         setting = session.query(Setting).selectfirst_by( Setting.c.var==param_in )
      else:
         setting = session.query(Setting).selectfirst_by( Setting.c.var==param_in, Setting.c.channel_id==channel )
      if setting is None:
         # The parameter was not found in the database. Do we have a default?
         if default is not None:
            # yes, we have a default. Return that instead the database value.
            return default
         else:
            log.msg( "\nRequired parameter %s was not found in the settings table!" % param_in )
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

# ----------------------------------------------------------------------------
# Table definitions
# ----------------------------------------------------------------------------

metadata = BoundMetaData(dburi, encoding='utf-8', echo=True)
if int(config['core.debug']) > 0:
   log.msg( "Echoing database queries" )
   metadata.engine.echo = True
else:
   metadata.engine.echo = False

channelTable   = Table( 'channel', metadata,
      Column( 'name', Unicode(32) ),
      Column( 'backend', Unicode(64) ),
      Column( 'backend_params', Unicode() ),
      autoload=True )
settingTable   = Table( 'setting', metadata,
      Column( 'value', Unicode()),
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

   def __init__( self, name, artist ):
      self.name  = name
      self.artist_id = artist.id
      self.added = datetime.now()

   def __repr__(self):
      return "<Album %s name=%s>" % (self.id, repr(self.name))

class Song(object):
   def __init__( self, localpath, artist, album ):
      self.localpath = localpath
      self.artist_id = artist.id
      self.added = datetime.now()
      if album is not None:
         self.album_id  = album.id

   def __repr__(self):
      return "<Song %s path=%s>" % (self.id, repr(self.localpath))

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

   def __init__( self, songid ):
      self.song_id = songid
      self.time_played = datetime.utcnow()

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
