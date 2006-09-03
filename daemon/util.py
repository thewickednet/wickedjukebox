from sqlobject.main import SQLObjectNotFound
from datetime import datetime
from model import *
from player import *
import md5

def get_hash(filename):
   """
   Return md5 hash.
   https://gumuz.looze.net/svn/gumuz/dupes/dupes.py
   """
   f = open(filename,'rb')
   hsh = md5.new()
   while 1:
      data = f.read(2048)
      if not data: break
      hsh.update(data)
   f.close()
   return hsh.hexdigest()

def getSetting(param_in, default=None):
   """
   Retrieves a setting from the database.

   PARAMETERS
      param_in - The name of the setting as string
      default  - (optional) If it's set, it provides the default value in case
                 the value was not found in the database.
   """
   try:
      return Settings.byParam(param_in).value
   except SQLObjectNotFound, ex:
      # The parameter was not found in the database. Do we have a default?
      if default is not None:
         # yes, we have a default. Return that instead the database value.
         return default
      else:
         # no, no default specified. This won't work so we tell the user
         words = str(ex).split()
         print
         print "Required parameter %s was not found in the settings table!" % words[6]
         print
         raise
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

def getArtist(artistName):
   """
   If the artist does not yet exist, create it. Otherwise get the database
   reference.

   PARAMETERS
      artistName - The name of the artist to create/retrieve

   RETURNS
      an Artists sql-object
   """

   if artistName is None or artistName == '':
      return None

   if Artists.selectBy(name=artistName).count() == 0:
      return Artists(
         name = artistName,
         added = datetime.datetime.now()
         )
   else:
      return Artists.selectBy(name=artistName)[0]

def getGenre(genreName):
   """
   If the genre does not yet exist, create it. Otherwise get the database
   reference.

   PARAMETERS
      genreName - The name of the genre to create/retrieve

   RETURNS
      an Genres ssql-object
   """

   if genreName is None or genreName == '':
      return None

   if Genres.selectBy(name=genreName).count() == 0:
      return Genres( name = genreName)
   else:
      return Genres.selectBy(name=genreName)[0]

def getAlbum(artistName, albumName):
   """
   If the album does not yet exist, create it. Otherwise get the database
   reference.

   PARAMETERS
      artistName - The name of the artist of that album
      albumName  - The name of the album to create/retrieve

   RETURNS
      an Albums sql-object
   """

   dbArtist = getArtist(artistName)

   if albumName is None or albumName == '' or dbArtist is None:
      return None

   if Albums.selectBy(title=albumName).count() == 0:
      album = Albums(
         title = albumName,
         added=datetime.datetime.now(),
         played = 0,
         downloaded = 0,
         type = 'album',
         artist=dbArtist
         )
      return album
   else:
      # check if we have the album with the matching artist
      album = list(Albums.selectBy(title=albumName))[0]
      if dbArtist == album.artist:
         return album
      # aha! we have an album with a matching name, but not the artist. that
      # means this is a "various artist" album, so update it and return it
      if album.type == 'album':
         album.type='various'
      return album

