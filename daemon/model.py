from sqlobject import *
sqlhub.processConnection = connectionForURI('mysql://wjb:wjb@localhost/wjb')
class CommandQueue(SQLObject):
   timeStamp = DateTimeCol()
   actor   = StringCol(length=64)
   command = StringCol(length=64)

class Settings(SQLObject):

   param = StringCol(length=16, alternateID=True)
   value = StringCol()

class Songs(SQLObject):

   class sqlmeta:
      idName = 'song_id'

   artist_id  = IntCol()
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
