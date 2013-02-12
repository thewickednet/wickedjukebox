import os
import threading
from datetime import datetime
import shout
import urllib2
import re
from hashlib import md5

import logging
LOG = logging.getLogger(__name__)

STATUS_STOPPED = 1
STATUS_PLAYING = 2
STATUS_PAUSED = 3
SONG_STARTED = None
__KEEP_RUNNING = True
__PORT = None
__MOUNT = None
__PASSWORD = None
__ADMIN_URL = None
__ADMIN_USER = None
__ADMIN_PASSWORD = None
__CHANNEL_ID = 0
__QUEUE = []
__SERVER = None
__CURRENT_SONG = None
__STREAMER = None


def init():
    pass


def release():
    pass


class Streamer(threading.Thread):

    def __init__(self, filename, server, channel_id):
        self.__keep_running = True
        self.__filename = filename
        self.__server = server
        self.__channel_id = channel_id
        self.__progress = (0, os.stat(filename).st_size)
        threading.Thread.__init__(self)

    def position(self):
        """
        Returns a percentage of how far we are in the song
        """
        # TODO: do some real calculations with bitrate (CBR & VBR) to return
        #       the position in seconds!
        try:
            return (float(self.__progress[0]) /
                    float(self.__progress[1]) *
                    100.0)
        except ZeroDivisionError:
            return 0

    def status(self):
        if self.isAlive():
            return "playing"
        else:
            return "stop"

    def stop(self):
        self.__keep_running = False

    def run(self):
        from wickedjukebox.demon.dbmodel import State
        LOG.debug("Starting to stream %r..." % self.__filename)
        fp = open(self.__filename, "rb")
        chunk = fp.read(1024)
        count = 0

        try:
            while self.__keep_running and chunk:
                self.__server.send(chunk)
                self.__server.sync()
                self.__progress = (self.__progress[0] + len(chunk),
                        self.__progress[1])
                chunk = fp.read(1024)

                if count % 100 == 0:  # TODO: Ticket #13
                    State.set("progress", self.position(), self.__channel_id)

                count += 1

        except KeyboardInterrupt:
            LOG.warn("Keyboard interrupt caught....")
            for thread in threading.enumerate():
                if isinstance(thread, threading._Timer):
                    thread.cancel()
            self.__keep_running = False

        LOG.debug("Shoutcast stream finished")
        fp.close()
        self.__server.sync()


def config(params):
    global __PORT, \
            __MOUNT, \
            __PASSWORD, \
            __STREAMER, \
            __ADMIN_URL, \
            __ADMIN_USER, \
            __ADMIN_PASSWORD, \
            __CHANNEL_ID
    LOG.info("connection to icecast server (params = %s)" % params)
    __PORT = int(params['port'])
    __MOUNT = str(params['mount'])
    __PASSWORD = str(params['pwd'])
    __CHANNEL_ID = int(params['channel_id'])

    if "admin_url" in params:
        __ADMIN_URL = (str(params["admin_url"]) +
                "/listclients.xsl?mount=" +
                __MOUNT)

    if "admin_username" in params:
        __ADMIN_USER = str(params["admin_username"])

    if "admin_password" in params:
        __ADMIN_PASSWORD = str(params["admin_password"])


def cropPlaylist(length=2):
    """
    Removes items from the *beginning* of the playlist to ensure it has only
    a fixed number of entries.

    @type  length: int
    @param length: The new size of the playlist
    """
    LOG.debug("Cropping pl to %d songs" % length)
    global __QUEUE
    if len(__QUEUE) <= length:
        return True

    __QUEUE = __QUEUE[-length:]
    return True


def getPosition():
    # returning as a percentage value

    if not __STREAMER:
        return (0, 100)

    try:
        return (int(__STREAMER.position()), 100)
    except TypeError:
        import traceback
        traceback.print_exc()
        LOG.warning("%r was not a valid number" % __STREAMER.position())
        return 0


def getSong():
    return __CURRENT_SONG


def queue(filename):
    from wickedjukebox.demon.dbmodel import Setting
    global SONG_STARTED
    LOG.debug("Received a queue (%s)" % filename)
    if Setting.get('sys_utctime', 0) == 0:
        SONG_STARTED = datetime.utcnow()
    else:
        SONG_STARTED = datetime.now()

    __QUEUE.append(filename)


def skipSong():
    LOG.debug("Received a skip request")
    stopPlayback()
    startPlayback()


def stopPlayback():
    from wickedjukebox.demon.dbmodel import State
    global __PROGRESS, __CURRENT_SONG, __STREAMER, __SERVER

    LOG.debug("Stopping playback")
    __CURRENT_SONG = None
    __PROGRESS = (0, 0)
    if __STREAMER:
        __STREAMER.stop()
        __STREAMER.join()

    if __SERVER:
        try:
            __SERVER.close()
        except shout.ShoutException as exc:
            LOG.warning('Unable to close connection: %s' % exc)
        __SERVER = None
    LOG.debug("Playback stopped")

    State.set("progress", 0, __CHANNEL_ID)


def pausePlayback():
    pass


def startPlayback():
    from wickedjukebox.demon.dbmodel import State
    global __QUEUE, __CURRENT_SONG, __SERVER

    LOG.info("Starting playback")
    State.set("progress", 0, __CHANNEL_ID)
    if not __QUEUE:
        LOG.warn("Nothing on queue.")
        return False

    if not __SERVER:
        LOG.warn("No icecast connection available!")
        __SERVER = __ic_connect()

    __CURRENT_SONG = __QUEUE.pop(0)
    __stream_file(__SERVER, __CURRENT_SONG)


def status():
    if __STREAMER:
        return __STREAMER.status()
    else:
        return "stopped"


def current_listeners():
    """
    Scrape the Icecast admin page for current listeners and return a list of
    MD5 hashes of their IPs
    """

    if (__ADMIN_URL is None or
        __ADMIN_USER is None or
        __ADMIN_PASSWORD is None):
        # not all required backend parameters supplied
        LOG.warning("Not all parameters set for screen scraping icecast "
                "statistics. Need admin-url and admin-password")
        return

    int_octet = "25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]?"
    p = re.compile(r"(((%s)\.){3}(%s))" % (int_octet, int_octet))

    # Create an OpenerDirector with support for Basic HTTP Authentication...
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password(realm='Icecast2 Server',
                              uri=__ADMIN_URL,
                              user=__ADMIN_USER,
                              passwd=__ADMIN_PASSWORD)
    opener = urllib2.build_opener(auth_handler)
    # ...and install it globally so it can be used with urlopen.
    urllib2.install_opener(opener)

    try:
        LOG.debug("Opening %r" % __ADMIN_URL)
        handler = urllib2.urlopen(__ADMIN_URL)
        data = handler.read()

        listeners = [md5(x[0]).hexdigest() for x in p.findall(data)]
        return listeners
    except urllib2.HTTPError, ex:
        LOG.error("Error opening %r: Caught %r" % (__ADMIN_URL, str(ex)))
        return None
    except urllib2.URLError, ex:
        LOG.error("Error opening %r: Caught %r" % (__ADMIN_URL, str(ex)))
        return None


def __ic_connect(name="The wicked jukebox", url="http://jukebox.wicked.lu",
        bufsize=1024, bitrate=128, samplerate=44100, channels=1):
    """
    Return a conenction to an icecast server

    TODO: This method's parameter should all be removed and set with the
          "config" method above (see Task #12)
    """
    server = shout.Shout()
    server.format = 'mp3'
    server.audio_info = {
            "bitrate": str(bitrate),
            "samplerate": str(samplerate),
            "channels": str(channels)}
    server.user = "source"
    server.name = name
    server.url = url
    server.password = __PASSWORD
    server.mount = __MOUNT
    server.port = __PORT
    server.open()
    return server


def __stream_file(server, filename):
    """
    Stream a file to a icecast backend

    @raises IOError: When unable to open the file
    """
    global __STREAMER
    __STREAMER = Streamer(filename, server, __CHANNEL_ID)
    __STREAMER.start()


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.DEBUG)
    sys.path.insert(0, os.getcwd())
    if len(sys.argv) < 2:
        print """
        USAGE: %s <filename>
        """ % sys.argv[0]
        sys.exit(1)

    if len(sys.argv) > 2:
        threading.Timer(float(sys.argv[2]), stopPlayback).start()

    config(dict(
          port=8001,
          mount="/wicked.mp3",
          pwd="mussdulauschtren",
          channel_id=1
       ))

    LOG.debug("Connecting to icecast...")
    __SERVER = __ic_connect()
    LOG.debug("Connected on %r" % __SERVER)
    queue(sys.argv[1])
    startPlayback()
