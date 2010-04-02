"""
Abstraction Layer for mutagen

Mutagen exposed the internal metadata as stored in the original file. This
causes an inconsistent external interface (f. ex. the "title" field is not
accessed in the same way for MP3 files as for FLAC files).

This module provides the necessary abstraction to handle all files identically

This modul is also executable and can be used to display meta information of a
specific file.
"""

import logging
from datetime import date
from mutagen.mp3 import MP3
from mutagen.id3 import ID3TimeStamp

# The class logger
LOG = logging.getLogger( __name__ )

# Keys which are shared among different file types. Other filetypes may extend
# on this
WELL_KNOWN_KEYS = [
         "title",
         "artist",
         "comment",
         "release_date",
         "track_no",
         "total_tracks",
         "album",
         "genres",
         "duration",
         "bitrate",
      ]

class AudioMeta( dict ):
   """
   Wraps Mutagen metadata and exposes it as a standardised dictionary
   """

   def __init__(self, mutagen_meta):
      """
      Initialises the class

      @param mutagen_meta: The mutagen metadata
      """
      self.meta = mutagen_meta
      self._keys = WELL_KNOWN_KEYS
      dict.__init__(self)

   def values(self):
      "@overrides dict.values"
      return [ self.__getitem__( key ) for key in self._keys ]

   def keys(self):
      "@overrides dict.keys"
      return self._keys

   def items(self):
      "@overrides dict.items"
      return zip( self.keys(), self.values() )

   def __getitem__( self, key ):
      "@overrides dict.__getitem__"
      accessor = self.__getattribute__( "get_%s" % key )
      return accessor()

   def __len__( self ):
      "@overrides dict.__len__"
      return len(self._keys)

   def __repr__( self ):
      "@overrides dict.__repr__"
      reprdict = {}
      for key, value in self.items():
         reprdict[key] = value
      return reprdict.__repr__()

   # -------------------------------------------------------------------------

   def get_artist(self):
      return "Unimplemented meta-info"

   def get_title(self):
      return "Unimplemented meta-info"

   def get_release_date( self ):
      return "Unimplemented meta-info"

   def get_comment( self ):
      return "Unimplemented meta-info"

   def get_track_no( self ):
      return "Unimplemented meta-info"

   def get_total_tracks( self ):
      return "Unimplemented meta-info"

   def get_album( self ):
      return "Unimplemented meta-info"

   def get_duration( self ):
      return "Unimplemented meta-info"

   def get_genres( self ):
      return ["Unimplemented meta-info"]

   def get_bitrate( self ):
      return "Unimplemented meta-info"

class MP3Meta( AudioMeta ):

   def decode_text( self, data ):
      import codecs

      if isinstance( data.text[0], ID3TimeStamp):
         text = "".join( [ x.text for x in data.text] )
      else:
         text = "".join( data.text )

      if data.encoding == 0:
         # latin-1
         return text
      elif data.encoding == 1 or data.encoding == 2:
         # utf16 or utf16be
         encoded = text.encode("utf_16_le")
         if encoded.startswith( codecs.BOM_UTF16_BE ) or encoded.startswith( codecs.BOM_UTF16_LE ):
            return encoded[2:].replace("\x00", "").decode("utf8")
      elif data.encoding == 3:
         # utf8
         return text
      else:
         raise NotImplementedError( "Unknown character encoding (enoding=%s)" % data.encoding )

   def get_release_date(self):
      if "TDRC" not in self.meta:
         return None

      data = self.meta["TDRC"]
      raw_string = self.decode_text( data )
      elements = raw_string.split("-")

      try:
         if len(elements) == 1:
            return date(int(elements[0]), 1, 1)
         elif len(elements) == 2:
            return date(int(elements[0]), int(elements[1]), 1)
         elif len(elements) == 3:
            return date(int(elements[0]), int(elements[1]), int(elements[2]))
      except ValueError, e:
         LOG.warning("%s (datestring was %s)" % (e, raw_string))
         return None

   def get_title(self):
      data = self.meta["TIT2"]
      return self.decode_text( data )

   def get_artist(self):
      return self.decode_text( self.meta["TPE1"] )

   def get_track_no( self ):
      tmp = self.decode_text( self.meta["TRCK"] ).split("/")
      return int( tmp[0] )

   def get_total_tracks( self ):
      tmp = self.decode_text( self.meta["TRCK"] ).split("/")
      if len( tmp ) > 1:
         return int( tmp[1] )

   def get_album( self ):
      return self.decode_text( self.meta["TALB"] )

   def get_genres( self ):
      try:
         return [self.decode_text( self.meta["TCON"] )]
      except KeyError:
         return []

   def get_duration( self ):
      return self.meta.info.length

   def get_bitrate( self ):
      return self.meta.info.bitrate

class MetaFactory(object):
   """
   Factory to create the proper AudioMeta instance depending on filetype
   """

   @classmethod
   def create( self, filename ):
      from mutagen import File
      try:
         mutagen_meta = File( filename )
      except IOError, e:
         LOG.error( e )
         return None

      if isinstance( mutagen_meta, MP3 ):
         abstract_meta = MP3Meta( mutagen_meta )
         return abstract_meta
      else:
         raise NotImplementedError( "This filetype (%s) is not yet implemented" % type(mutagen_meta))

def display_file( filename ):
   metadata = MetaFactory.create( filename )

   if metadata is None:
      return

   print 79*"-"
   print filename
   print 79*"-"
   for key in metadata.keys():
      print "%-15s | %s" % ( key, metadata[key] )
   print 79*"-"

if __name__ == "__main__":
   import sys
   logging.basicConfig()
   if len( sys.argv ) != 2:
      print """Usage:
         %s <filename>
      """ % sys.argv[0]
      sys.exit(9)
   display_file( sys.argv[1] )

