from sqlalchemy import *
from util import config
from datetime import datetime

if config['database.type'] == 'sqlite':
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

# ----------------------------------------------------------------------------
# Table definitions
# ----------------------------------------------------------------------------

metadata = BoundMetaData(dburi, encoding='utf-8', echo=True)
if int(config['core.debug']) > 0:
   print "Echoing database queries"
   metadata.engine.echo = True
else:
   metadata.engine.echo = False

playmodeTable = Table( 'playmode', metadata, autoload=True )
channelTable  = Table( 'channel', metadata, autoload=True )
settingTable  = Table( 'setting', metadata, autoload=True )
artistTable   = Table( 'artist', metadata, autoload=True )
albumTable    = Table( 'album', metadata, autoload=True )
songTable     = Table( 'song', metadata, autoload=True )

# ----------------------------------------------------------------------------
# Mappers
# ----------------------------------------------------------------------------

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

   def __repr__(self):
      return "<Album %s name=%s>" % (self.id, repr(self.name))

class Song(object):
   def __init__( self, localpath, artist, album ):
      self.localpath = localpath
      self.artist_id = artist.id
      if album is not None:
         self.album_id  = album.id

   def __repr__(self):
      return "<Song %s path=%s>" % (self.id, repr(self.localpath))


mapper(Setting, settingTable)
mapper(Channel, channelTable)
mapper(Album, albumTable, properties=dict(
   songs=relation(Song, backref='album')))

mapper(Artist, artistTable, properties=dict(
   albums=relation(Album, backref='artist'),
   songs = relation(Song, backref='artist')
   ))
mapper(Song, songTable)
