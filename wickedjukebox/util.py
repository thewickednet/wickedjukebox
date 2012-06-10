"""
Utility methods
"""

import sys, os
import ConfigParser
import logging
LOG = logging.getLogger(__name__)

ENCODINGS = [
   'latin-1',
   'utf-8',
   sys.getfilesystemencoding(),
]

FS_CODING = sys.getfilesystemencoding()

# prepare encodings in reversed order for fs-encoding
REVENCODINGS = ENCODINGS
REVENCODINGS.reverse()

def fsencode(filename):
   if not isinstance( filename, unicode ):
      # no need to re-encode
      return filename

   try:
      return filename.encode( FS_CODING )
   except UnicodeEncodeError, e:
      LOG.error( "Filename %r is not encoded using the registered filesystem encoding!" % filename )
      return None

def fsdecode(filename):
   LOG.debug("Trying to decode %r using %r." % (filename, FS_CODING))
   if isinstance( filename, unicode ):
      # no need to redecode
      return filename

   try:
      decoded = (filename.decode( FS_CODING ), FS_CODING)
      LOG.debug( "Encoded as %r - %r" % decoded )
   except UnicodeDecodeError, e:
      LOG.error("Filename %r is not encoded using the registered filesystem encoding!" % filename)
      return (None, None)
   return decoded

def fsencode_old(filename):
   """
   Encodes a unicode object into the file system encoding
   """

   global REVENCODINGS
   revencodings = REVENCODINGS[:] # keep a copy

   if type(filename) == type(u""):
      encoded = None
      while True:
         try:
            if not revencodings: break
            encoding = revencodings.pop()
            encoded = filename.encode(encoding)
            working_charset = encoding
            LOG.debug( "encoded %r with %r" % ( filename, encoding ) )
            break
         except UnicodeEncodeError, e:
            LOG.warning("File %r uses an unexpected encoding. %r did not work to encode it. Will try another encoding" % (filename, encoding))
            return filename.encode(sys.getfilesystemencoding())
      if len(filename) > 0 and not encoded:
         raise UnicodeEncodeError("Unable to encode %r" % filename)
      return encoded
   else:
      return filename

def fsdecode_old(filename):
   """
   Decodes a filename, returning it's decoded name with the used charset
   Raises an UnicodeDecodeError if decoding did not work
   """
   global ENCODINGS

   decoded = None

   working_charset = None

   # make a copy of the global encodings list so we can pop items off
   encodings = ENCODINGS[:]

   while True:
      try:
         if not encodings: break
         encoding = encodings.pop()
         decoded = filename.decode(encoding)
         working_charset = encoding
         LOG.debug( "decoded %r with %r" % ( filename, encoding ) )
         break
      except UnicodeDecodeError:
         LOG.warning("File %r uses an unexpected encoding. %r did not work to decode it. Will try another encoding" % (filename, encoding))

   if not decoded:
      raise UnicodeDecodeError("Unable to decode %r" % filename)

   return decoded, working_charset

def direxists(dir):
   import os.path
   if not os.path.exists( dir ):
      LOG.warning( "'%s' does not exist!" % dir )
      return False
   else:
      return True
