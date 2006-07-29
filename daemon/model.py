from sqlobject import *

import ConfigParser
import string

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

   artist     = ForeignKey('artists')
   title      = StringCol(length=128)
   ##duration   time     No    00:00:00
   genre_id   = IntCol()
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

dburi = "%s://%s:%s@%s/%s" % (
      config['database.dbms'],
      config['database.user'],
      config['database.password'],
      config['database.host'],
      config['database.name'],
      )

sqlhub.processConnection = connectionForURI(dburi)
