from sqlobject import *

import ConfigParser
import string, datetime

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
   "database.dbms":     "mysql",
   "database.name":     "wjukebox",
   "database.user":     "wjb",
   "database.password": "wjb",
   "database.host":     "127.0.0.1"
}

config = LoadConfig("db.ini", _ConfigDefault)

class Settings(SQLObject):

   param = StringCol(length=16, alternateID=True)
   value = StringCol()

class Songs(SQLObject):

   class sqlmeta:
      idName = 'song_id'

   albums     = RelatedJoin('Albums', intermediateTable='album_song', joinColumn='song_id', otherColumn='album_id')

   artist     = MultipleJoin('Artists', joinColumn='artist_id')
   title      = StringCol(length=128)
   #duration   time     No    00:00:00
   genre      = MultipleJoin('Genres', joinColumn='genre_id')
   year       = StringCol(length=4)
   localpath  = StringCol()
   played     = IntCol()
   voted      = IntCol()
   skipped    = IntCol()
   downloaded = IntCol()
   added      = DateTimeCol()
   bitrate    = StringCol(length=8)
   filesize   = IntCol()
   checksum   = StringCol(length=32)
   lyrics     = StringCol()
   dirty      = BoolCol()

class Albums(SQLObject):

   class sqlmeta:
      idName = 'album_id'

   songs   = RelatedJoin('Songs', intermediateTable='album_song', joinColumn='album_id', otherColumn='song_id')
   title   = StringCol(length=128)
   added   = DateTimeCol()
   artists = MultipleJoin('Artists', joinColumn='artist_id')

class Channels(SQLObject):

   class sqlmeta:
      idName = 'channel_id'

   name           = StringCol(length=32)
   public         = BoolCol()
   backend        = StringCol(length=32)
   backend_params = StringCol()

class Genres(SQLObject):

   class sqlmeta:
      idName = 'genre_id'

   name = StringCol(length=64)

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
   user     = MultipleJoin('Users', joinColumn='user_id')
   public   = BoolCol()
   added    = DateTimeCol()

class Queue(SQLObject):

   class sqlmeta:
      idName = 'queue_id'

   songs      = MultipleJoin('Songs', joinColumn='song_id')
   users      = MultipleJoin('Users', joinColumn='user_id')
   channel    = MultipleJoin('Channels', joinColumn='channel_id')
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

# ----------------------------------------------------------------------------

dburi = "%s://%s:%s@%s/%s" % (
      config['database.dbms'],
      config['database.user'],
      config['database.password'],
      config['database.host'],
      config['database.name'],
      )

sqlhub.processConnection = connectionForURI(dburi)

