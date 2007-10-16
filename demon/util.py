import os,ConfigParser, threading
from twisted.python import log
import urllib, httplib, md5, time, sys
import scrobbler

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

# load the configuration file, and set up the DB-conenction
config = loadConfig(os.path.join('config.ini'))

class Scrobbler(threading.Thread):

   """
   Submits tracks to last.fm. It does not submit more than one song per minute
   to easen last.fm's load
   """

   __keepRunning = True

   def __init__(self, user, passwd):
      """
      Constructor
      """
      threading.Thread.__init__(self)
      self.setName( '%s (%s)' % (self.getName(), 'Scro') )

      self.__user   = user
      self.__passwd = passwd

      try:
         scrobbler.login( user, passwd )
      except scrobbler.AuthError:
         print "problem authencitating with AS. Stopping service."
         self.__keepRunning = False

   def now_playing( self, artist, track, album="", length="", trackno="", mbid="" ):
      scrobbler.now_playing( artist, track, album, length, trackno, mbid )

   def run(self):
      """
      The main control loop of the Scrobbler.
      It checks once a minute if there are new songs on the scrobbler queue
      that should be submitted, then submits them.
      """

      from model import LastFMQueue, lastfmTable, create_session

      log.msg( "Scrobbler started" )

      sess = create_session()
      while self.__keepRunning:
         nextScrobble = sess.query(LastFMQueue).selectfirst(order_by=lastfmTable.c.queue_id)
         if nextScrobble is not None:
            res = scrobbler.submit(
                  artist  = nextScrobble.song.artist.name,
                  track   = nextScrobble.song.title,
                  time    = int(time.mktime(nextScrobble.time_played.timetuple())),
                  length  = int(nextScrobble.song.duration),
                  album   = nextScrobble.song.album.name,
                  trackno = nextScrobble.song.track_no,
                  autoflush = True
                  )
            if res is True:
               log.msg( "Successfully scrobbled %s - %s" % (nextScrobble.song.artist.name, nextScrobble.song.title) )
               sess.delete(nextScrobble)
            else:
               log.msg("Something went wrong when scrobbling")
         sess.flush()
         time.sleep(5)
      sess.close()
      log.msg( "Scrobbler stopped" )

   def stop(self):
      self.__keepRunning = False

if config.has_key( 'filesystem.force_encoding' ):
   fs_encoding = config['filesystem.force_encoding']
else:
   fs_encoding = sys.getfilesystemencoding()
