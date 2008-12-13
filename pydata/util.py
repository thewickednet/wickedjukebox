"""
Utility methods
"""

import sys
import logging
logger = logging.getLogger(__name__)

def fsencode(filename):
   """
   Encodes a unicode object into the file system encoding
   """
   if type(filename) == type(u""):
      return filename.encode(sys.getfilesystemencoding())
   else:
      return filename

def fsdecode(filename):
   """
   Decodes a filename, returning it's decoded name with the used charset
   Raises an UnicodeDecodeError if decoding did not work
   """
   decoded = None

   encodings = [
      'latin-1',
      'utf-8',
      sys.getfilesystemencoding(),
   ]

   working_charset = None

   while True:
      try:
         if len(encodings) == 0: break
         encoding = encodings.pop()
         decoded = filename.decode(encoding)
         working_charset = encoding
         logger.debug( "decoded %r with %r" % ( filename, encoding ) )
         break
      except UnicodeDecodeError:
         logger.warning("File %r uses an unexpected encoding. %r did not work to decode it. Will try another encoding" % (filename, encoding))

   if decoded is None:
      raise UnicodeDecodeError("Unable to decode %r" % filename)

   return decoded, working_charset

