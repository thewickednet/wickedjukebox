from sqlobject import *

import ConfigParser
import string, datetime, os

def LoadConfig(file, config={}):
    """
    returns a dictionary with key's of the form
    <section>.<option> and the values 

    from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65334
    """
    config = config.copy()
    cp = ConfigParser.ConfigParser()
    cp.read(file)
    for sec in cp.sections():
        name = string.lower(sec)
        for opt in cp.options(sec):
            config[name + "." + string.lower(opt)] = string.strip(cp.get(sec, opt))
    return config

_ConfigDefault = {
   "Database.Type":     "mysql",
   "Database.Base":     "wjukebox",
   "Database.User":     "wjb",
   "Database.Pass":     "wjb",
   "Database.Host":     "127.0.0.1"
}

config = LoadConfig(os.path.join("..", "phpdata", "config.ini"), _ConfigDefault)

class Settings(SQLObject):

   class sqlmeta:
      idName = 'setting_id'

   param = StringCol(length=16, alternateID=True)
   value = StringCol()

class AlbumSong(SQLObject):
   class sqlmeta:
      table='album_song'
   track    = IntCol()
   song_id  = IntCol()
   album_id = IntCol()

class Songs(SQLObject):

   class sqlmeta:
      idName      = 'song_id'
      lazyUpdates = True # only save changes when calling "sync"

   albums     = RelatedJoin('Albums', intermediateTable='album_song', joinColumn='song_id', otherColumn='album_id')

   artist     = ForeignKey('Artists', dbName='artist_id')
   title      = StringCol(length=128)
   #duration   time     No    00:00:00
   genre      = ForeignKey('Genres', dbName='genre_id')
   year       = StringCol(length=4)
   localpath  = StringCol()
   played     = IntCol()
   voted      = IntCol()
   skipped    = IntCol()
   downloaded = IntCol()
   added      = DateTimeCol()
   lastPlayed = DateTimeCol(dbName='lastPlayed')
   bitrate    = StringCol(length=8)
   filesize   = IntCol()
   checksum   = StringCol(length=32)
   lyrics     = StringCol()
   isDirty    = BoolCol(dbName='dirty')
   queues     = MultipleJoin('QueueItem', joinColumn='song_id')

class Albums(SQLObject):

   class sqlmeta:
      idName = 'album_id'

   songs   = RelatedJoin('Songs', intermediateTable='album_song', joinColumn='album_id', otherColumn='song_id')
   title   = StringCol(length=128)
   added   = DateTimeCol()
   artist  = ForeignKey('Artists', dbName='artist_id')

class Channels(SQLObject):

   class sqlmeta:
      idName = 'channel_id'

   name           = StringCol(length=32)
   public         = BoolCol()
   backend        = StringCol(length=32)
   backend_params = StringCol()
   queues      = MultipleJoin('QueueItem', joinColumn='channel_id')

class Genres(SQLObject):

   class sqlmeta:
      idName = 'genre_id'

   name  = StringCol(length=64)
   songs = MultipleJoin('Songs', joinColumn='genre_id')

class Groups(SQLObject):

   class sqlmeta:
      idName = 'group_id'

   title         = StringCol(length=32)
   admin         = BoolCol()
   nocredits     = BoolCol()
   queue_skip    = BoolCol()
   queue_remove  = BoolCol()

class Playlist(SQLObject):

   class sqlmeta:
      idName = 'playlist_id'

   title    = StringCol(length=64)
   user     = ForeignKey('Users', dbName='user_id')
   public   = BoolCol()
   added    = DateTimeCol()

class QueueItem(SQLObject):

   class sqlmeta:
      table  = 'queue'
      idName = 'queue_id'

   song       = ForeignKey('Songs', dbName='song_id')
   user       = ForeignKey('Users', dbName='user_id')
   channel    = ForeignKey('Channels', dbName='channel_id')
   position   = IntCol()
   added      = DateTimeCol()

class Users(SQLObject):

   class sqlmeta:
      idName = 'user_id'

   username    = StringCol(length=32)
   password    = StringCol(length=32)
   fullname    = StringCol(length=64)
   added       = DateTimeCol()
   credits     = IntCol()
   playlists   = MultipleJoin('Playlist', joinColumn='user_id')
   queues      = MultipleJoin('QueueItem', joinColumn='user_id')

class Artists(SQLObject):

   class sqlmeta:
      idName = 'artist_id'

   name   = StringCol(length=128)
   albums = MultipleJoin('Albums', joinColumn='artist_id')
   songs  = MultipleJoin('Songs', joinColumn='artist_id')

# ----------------------------------------------------------------------------

dburi = "%s://%s:%s@%s/%s" % (
      config['Database.Type'],
      config['Database.User'],
      config['Database.Pass'],
      config['Database.Host'],
      config['Database.Base'],
      )

sqlhub.processConnection = connectionForURI(dburi)

