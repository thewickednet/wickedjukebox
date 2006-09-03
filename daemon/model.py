# ----------------------------------------------------------------------------
#  $Id$
# ----------------------------------------------------------------------------
#  This file contains the database model for the wicked jukebox. The data
#  definitions are based on SQLObject (www.swlobject.org). When it comes to
#  manually creating SQL queries, the documentation of SQLObject does not tell
#  you very much. A good complementary source is
#  http://www.groovie.org/articles/2005/11/01/how-to-use-database-agnostic-sql-in-sqlobject
# ----------------------------------------------------------------------------

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

class Settings(SQLObject):
   """
   Maps to the settings table. Nothing fancy here
   """

   class sqlmeta:
      idName = 'setting_id'

   #--- Fields ---------------------------------
   param = StringCol(length=16, alternateID=True)
   value = StringCol()

   #--- Foreign Keys ---------------------------
   user  = ForeignKey('Users', dbName='user_id')

class Songs(SQLObject):
   """
   The songs table.
   TODO: The duration field needs some work. No clue how to implement a "time"
         field in SQLObject yet
   """

   class sqlmeta:
      idName      = 'song_id'

   #--- Fields ---------------------------------
   trackNo     = IntCol(default=0)
   title       = StringCol(length=128)
   duration    = IntCol(default=0)
   year        = StringCol(length=4, default=None)
   localpath   = StringCol(length=255)
   played      = IntCol(default=0)
   voted       = IntCol(default=0)
   skipped     = IntCol(default=0)
   downloaded  = IntCol(default=0)
   added       = DateTimeCol(default=datetime.datetime.now())
   lastPlayed  = DateTimeCol(dbName='lastPlayed', default=None)
   lastScanned = DateTimeCol(dbName='lastScanned', default=None)
   bitrate     = StringCol(length=8, default='')
   filesize    = IntCol(default=0)
   checksum    = StringCol(length=32, default='')
   lyrics      = StringCol(default='')
   cost        = IntCol(default=5)
   isDirty     = BoolCol(dbName='dirty', default=True)

   #--- Foreign Keys ---------------------------
   artist     = ForeignKey('Artists', dbName='artist_id')
   album      = ForeignKey('Albums', dbName='album_id')
   genre      = ForeignKey('Genres', dbName='genre_id')

   #--- Joins ----------------------------------
   queues     = MultipleJoin('QueueItem', joinColumn='song_id')

class Albums(SQLObject):
   """
   The albums table
   """

   class sqlmeta:
      idName = 'album_id'

   #--- Fields ---------------------------------
   title      = StringCol(length=128)
   added      = DateTimeCol()
   played     = IntCol()
   downloaded = IntCol()
   type       = StringCol(length=19)

   #--- Foreign Keys ---------------------------
   artist     = ForeignKey('Artists', dbName='artist_id')

   #--- Joins ----------------------------------
   songs      = MultipleJoin('Songs', joinColumn='album_id')

class Channels(SQLObject):
   """
   The channels table
   """

   class sqlmeta:
      idName = 'channel_id'

   #--- Fields ---------------------------------
   name           = StringCol(length=32)
   public         = BoolCol()
   backend        = StringCol(length=32)
   backend_params = StringCol()
   active         = BoolCol()
   ping           = DateTimeCol()

   #--- Joins ----------------------------------
   queues         = MultipleJoin('QueueItem', joinColumn='channel_id')

class Genres(SQLObject):
   """
   The genres table
   """

   class sqlmeta:
      idName = 'genre_id'

   #--- Fields ---------------------------------
   name  = StringCol(length=64)

   #--- Joins ----------------------------------
   songs = MultipleJoin('Songs', joinColumn='genre_id')

class Groups(SQLObject):
   """
   The groups table
   """

   class sqlmeta:
      idName = 'group_id'

   #--- Fields ---------------------------------
   title         = StringCol(length=32)
   admin         = BoolCol()
   nocredits     = BoolCol()
   queue_add     = BoolCol()
   queue_remove  = BoolCol()
   queue_skip    = BoolCol()

   #--- Joins ----------------------------------
   users         = MultipleJoin('Users', joinColumn='group_id')

class QueueItem(SQLObject):
   """
   The queue table. I renamed it to QueueItem for clarity in the code.
   """

   class sqlmeta:
      table  = 'queue'
      idName = 'queue_id'

   #--- Fields ---------------------------------
   position   = IntCol()
   added      = DateTimeCol()

   #--- Foreign Keys ---------------------------
   song       = ForeignKey('Songs', dbName='song_id')
   user       = ForeignKey('Users', dbName='user_id')
   channel    = ForeignKey('Channels', dbName='channel_id')

class Users(SQLObject):
   """
   The users table
   """

   class sqlmeta:
      idName = 'user_id'

   #--- Fields ---------------------------------
   username    = StringCol(length=32)
   password    = StringCol(length=32)
   fullname    = StringCol(length=64)
   added       = DateTimeCol()
   credits     = IntCol()
   cookie      = StringCol(length=32)
   downloads   = IntCol()
   votes       = IntCol()
   skips       = IntCol()
   selects     = IntCol()

   #--- Foreign Keys ---------------------------
   group       = ForeignKey('Groups', dbName='group_id')

   #--- Joins ----------------------------------
   queues      = MultipleJoin('QueueItem', joinColumn='user_id')
   settings    = MultipleJoin('Settings',  joinColumn='user_id')

class Artists(SQLObject):
   """
   The artists table
   """

   class sqlmeta:
      idName = 'artist_id'

   #--- Fields ---------------------------------
   name   = StringCol(length=128)
   added  = DateTimeCol()

   #--- Joins ----------------------------------
   albums = MultipleJoin('Albums', joinColumn='artist_id')
   songs  = MultipleJoin('Songs', joinColumn='artist_id')

# ----------------------------------------------------------------------------

# load the configuration file, and set up the DB-conenction
config = LoadConfig(os.path.join("..", "phpdata", "config.ini"))

dburi = "%s://%s:%s@%s/%s" % (
      config['database.type'],
      config['database.user'],
      config['database.pass'],
      config['database.host'],
      config['database.base'],
      )

sqlhub.processConnection = connectionForURI(dburi)

# vim: set ts=3 sw=3 ai :
