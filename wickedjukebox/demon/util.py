import os
import ConfigParser
import threading
import time
import sys
import logging

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
LOG = logging.getLogger(__name__)


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
        self.setName('%s (%s)' % (self.getName(), 'Scro'))

        self.__user = user
        self.__passwd = passwd

        try:
            scrobbler.login(user, passwd)
        except scrobbler.AuthError:
            import traceback
            traceback.print_exc()
            print "problem authencitating with AS. Stopping service."
            self.__keepRunning = False

    def now_playing(self, artist, track, album="", length="", trackno="",
            mbid=""):
        scrobbler.now_playing(artist, track, album, length, trackno, mbid)

    def run(self):
        """
        The main control loop of the Scrobbler.
        It checks once a minute if there are new songs on the scrobbler queue
        that should be submitted, then submits them.
        """

        from model import LastFMQueue, lastfmTable, create_session

        LOG.info("Scrobbler started")

        sess = create_session()
        while self.__keepRunning:
            nextScrobble = sess.query(LastFMQueue).selectfirst(
                    order_by=lastfmTable.c.queue_id)
            if nextScrobble is not None:
                while True:
                    try:
                        res = scrobbler.submit(
                                artist=nextScrobble.song.artist.name,
                                track=nextScrobble.song.title,
                                time=int(time.mktime(
                                    nextScrobble.time_played.timetuple())),
                                length=int(nextScrobble.song.duration),
                                album=nextScrobble.song.album.name,
                                trackno=nextScrobble.song.track_no,
                                autoflush=True
                                )
                        break
                    except Exception, ex:
                        import traceback
                        traceback.print_exc()
                        print ("Exception caught with Audioscrobbler "
                               "submission: %s" % str(ex))
                        time.sleep(1)

                if res is True:
                    LOG.info("Successfully scrobbled %s - %s" % (
                        nextScrobble.song.artist.name,
                        nextScrobble.song.title))
                    sess.delete(nextScrobble)
                else:
                    LOG.error("Something went wrong when scrobbling")
            sess.flush()
            time.sleep(5)
        sess.close()
        LOG.info("Scrobbler stopped")

    def stop(self):
        self.__keepRunning = False

if 'filesystem.force_encoding' in config:
    fs_encoding = config['filesystem.force_encoding']
else:
    fs_encoding = sys.getfilesystemencoding()
