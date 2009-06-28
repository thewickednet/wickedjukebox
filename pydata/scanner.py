"""
Audio file scanner module

This module contains everything needed to scan a directory of audio files an
store the metadata in the jukebox database
"""
from os import walk, path
from util import fsdecode, fsencode
import logging
from demon.model import getSetting, Song, songTable
from sqlalchemy import create_session, select
from filescan import scan as fscan
logger = logging.getLogger(__name__)

valid_extensions = getSetting("recognizedTypes").split(" ")

def is_valid_audio_file(path):
   return path.endswith(valid_extensions[0])

def do_housekeeping():
   "Database cleanup, and set other values that are difficult to read during scanning"
   logger.info( "Performing housekeeping. This may take a while!" )
   songs = select([songTable.c.localpath]).execute()
   for row in songs:
      try:
         if not path.exists( fsencode(row[0]) ):
            print `row[0]`, "removed from disk"
      except UnicodeEncodeError, e:
         logger.error( "Unable to decode %r (%s)" % ( row[0], e) )

def process(localpath, encoding):

   if is_valid_audio_file(localpath):
      session = create_session()
      song = session.query(Song).selectfirst_by( localpath=localpath )
      if not song:
         song = Song(localpath, None, None)
      song.scan_from_file( localpath, encoding )
      session.save_or_update(song)
      session.flush()

      logger.debug( "%r at %r" % (song, localpath) )
   else:
      logger.debug("%r is not a valid audio-file (only scanning extensions %r)" % (localpath, valid_extensions))

def filter_capping( root, filename, capping ):
   relative_path = filename[len(root)+1:]
   return not relative_path.startswith(capping)

def filter_valid_extenstion( root, filename ):
   extinfo = os.path.splitext( filename )
   if not extinfo:
      logger.warn("Unable to split extension from file %r. This file will be ignored!" % filename )
      return True
   else:
      extension = extinfo[1].replace(".", "")
      if extension not in valid_extensions:
         logger.info("%r is not a valid audio-file (only scanning extensions %r)" % (filename, valid_extensions))
         return True
   return False

def processor_todatabase(root, localpath):
   session = create_session()
   song = session.query(Song).selectfirst_by( localpath=localpath )
   if not song:
      song = Song(localpath, None, None)
   song.scan_from_file( localpath, encoding )
   session.save_or_update(song)
   session.flush()
   logger.debug( "%r at %r" % (song, localpath) )

def scan(top, capping=u""):
   """
   Scans a folder rootet at <top> for audio files. It will only include files starting with <capping>

   @param top: The root folder to scan
   @param capping: Only scan top-level folders starting with this string
   """
   logger.info("Starting scan on %r with capping %r" % (top, capping))

   top = fsencode(top)
   capping = fsencode(capping)
   count = fscan( top,
          filters=[ (filter_capping, capping), filter_valid_extenstion ],
          processors = [ processor_todatabase ]
          )
   logger.info( "Scanned %d songs" % count )

