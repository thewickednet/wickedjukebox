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

# prepare encodings in reversed order for fs-encoding
REVENCODINGS = ENCODINGS
REVENCODINGS.reverse()

def fsencode(filename):
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

def fsdecode(filename):
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

def loadConfig(file, config={}):
    """
    returns a dictionary with key's of the form
    <section>.<option> and the values.

    from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65334
    """
    if not os.path.exists( file ):
       raise ValueError, 'Cannot find configfile "%s"' % file
    config = config.copy()
    cp = ConfigParser.ConfigParser()
    cp.read(file)
    for sec in cp.sections():
        name = sec.lower()
        for opt in cp.options(sec):
            config[name + "." + opt.lower()] = cp.get(sec, opt).strip()
    return config

def direxists(dir):
   import os.path
   if not os.path.exists( dir ):
      LOG.warning( "'%s' does not exist!" % dir )
      return False
   else:
      return True
