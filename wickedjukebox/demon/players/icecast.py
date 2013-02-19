# TODO: Maybe it would be better to have a "global" atexit function properly
# TODO:    supervising stopping the threads.
import time
import os
from threading import Thread
from Queue import Empty, Queue
from datetime import datetime
from os import urandom
import shout
import urllib2
import re
from hashlib import md5
from wickedjukebox.demon.dbmodel import State
import atexit

import logging
LOG = logging.getLogger(__name__)

SCMD_QUEUE = 'queue'
SCMD_PAUSE = 'pause'
SCMD_SKIP = 'skip'
SCMD_START = 'start'
SCMD_STOP = 'stop'

STATUS_PAUSED = 'paused'
STATUS_STARTED = 'started'
STATUS_STOPPED = 'stopped'


class Player(object):

    LOG = logging.getLogger('{0}.Player'.format(__name__))

    def __init__(self, channel_id, icy_conf):
        Player.LOG.debug('Initialising with {0!r}, {1!r}'.format(channel_id,
            icy_conf))
        self.source_command = Queue()
        dataq = Queue()
        self.filereader = FileReader(self.source_command, dataq)
        self.provider = IceProvider(dataq, icy_conf)
        self.filereader.start()
        self.provider.start()
        # TODO: Set progress
        #    State.set("progress", self.position(), self.__channel_id)
        #    State.set("progress", 0, __CHANNEL_ID)

    def crop_playlist(self, max_items=2):
        Player.LOG.debug('Cropping playlist to {0} items'.format(max_items))
        self.filereader.crop_queue(max_items)

    def listeners(self):
        return self.provider.listener_ips()

    def position(self):
        Player.LOG.debug('Interpreting position {0!r}'.format(
            self.filereader.position))
        try:
            a, b = self.filereader.position
            return float(a) / float(b) * 100
        except ZeroDivisionError:
            return 0.0

    def current_song(self):
        return self.filereader.current_file

    def pause(self):
        self.source_command.put((SCMD_PAUSE, None))

    def queue(self, filename):
        self.source_command.put((SCMD_QUEUE, filename))

    def skip(self):
        self.source_command.put((SCMD_SKIP, None))

    def start(self):
        self.source_command.put((SCMD_START, None))

    def status(self):
        return self.filereader.status

    def stop(self):
        self.source_command.put((SCMD_STOP, None))


class FileReader(Thread):

    LOG = logging.getLogger('{0}.FileReader'.format(__name__))

    def __init__(self, qcmds, qdata, *args, **kwargs):
        FileReader.LOG.debug('Initialising with {0!r}, {1!r}, {2!r}, '
            '{3!r}'.format(qcmds, qdata, args, kwargs))
        super(FileReader, self).__init__(*args, **kwargs)
        self.qcmds = qcmds
        self.qdata = qdata
        self.daemon = True
        self.current_file = None
        self._stat = None
        self.chunk_size = 1024
        self.status = STATUS_STOPPED

    def run(self):
        FileReader.LOG.debug('Starting')
        do_skip = False
        song_queue = []
        while True:
            try:
                cmd, args = self.qcmds.get(False)
                FileReader.LOG.debug('Recieved command {0!r} '
                        'with args {1!r}'.format(cmd, args))
                if cmd == SCMD_QUEUE:
                    song_queue.append(args)
                elif cmd == SCMD_PAUSE:
                    self.status = (self.status == STATUS_PAUSED and
                                    STATUS_STARTED or
                                    STATUS_PAUSED)
                elif cmd == SCMD_SKIP:
                    do_skip = True
                elif cmd == SCMD_START:
                    self.status = STATUS_STARTED
                elif cmd == SCMD_STOP:
                    self.status = STATUS_STOPPED
            except Empty:
                pass

            if do_skip and song_queue:
                FileReader.LOG.debug('Skip requested on queue {0!r}'.format(
                    song_queue))
                new_file = song_queue.pop(0)
                self.closefile()
                self.openfile(new_file)
                FileReader.LOG.debug('Previous file closed and reopened '
                        'with {0!r}. Queue is now: {1!r}'.format(
                            new_file, song_queue))

            if not self.current_file and song_queue:
                FileReader.LOG.debug('No file currently open, but we have '
                        'a queue: {0!r}. Opening...'.format(song_queue))
                self.openfile(song_queue.pop(0))

            chunk = ''
            if self.current_file:
                chunk = self.current_file.read(self.chunk_size)
                FileReader.LOG.debug('Chunk of length {0} read from '
                        '{1!r}'.format(len(chunk), self.current_file.name))
                if not chunk:
                    self.closefile()

            if chunk and self.status not in (STATUS_STOPPED, STATUS_PAUSED):
                self.qdata.put(chunk)
            else:
                FileReader.LOG.debug('No chunk available. (status={0}) '
                    'Sending random data.'.format(self.status))
                self.qdata.put(urandom(self.chunk_size))

    def closefile(self):
        FileReader.LOG.debug('Closing {0!r}'.format(self.current_file))
        self.current_file.close()
        self.current_file = None
        self._stat = None

    def openfile(self, fname):
        FileReader.LOG.debug('Opening {0!r}'.format(fname))
        self.current_file = open(fname, 'rb')
        self._stat = os.stat(fname)

    def position(self):
        if self.current_file and self._stat:
            return (self.current_file.tell(), self._stat.st_size)
        else:
            return (0, 0)

    def crop_queue(self, max_items):
        # TODO: implement
        pass


class IceProvider(Thread):

    LOG = logging.getLogger('{0}.IceProvider'.format(__name__))

    def __init__(self, qin, params, *args, **kwargs):
        super(IceProvider, self).__init__(*args, **kwargs)
        self.qin = qin
        self.daemon = True
        LOG.info("connection to icecast server (params = %s)" % params)
        self.port = int(params['port'])
        self.mount = str(params['mount'])
        self.password = str(params['pwd'])
        self.admin_url = None
        self.admin_username = None
        self.admin_password = None

        if "admin_url" in params:
            self.admin_url = "{0}/listclients.xsl?mount={1}".format(
                    params['admin_url'],
                    self.mount)

        if "admin_username" in params:
            self.admin_user = params["admin_username"]

        if "admin_password" in params:
            self.admin_password = params["admin_password"]

        self._connect()
        atexit.register(self.disconnect)

    def _connect(self, name="The wicked jukebox",
            url="http://jukebox.wicked.lu", bufsize=1024, bitrate=128,
            samplerate=44100, channels=1):

        self._icy_handle = shout.Shout()
        self._icy_handle.format = 'mp3'
        self._icy_handle.audio_info = {
              "bitrate": str(bitrate),
              "samplerate": str(samplerate),
              "channels": str(channels)}
        self._icy_handle.user = "source"
        self._icy_handle.name = name
        self._icy_handle.url = url
        self._icy_handle.password = self.password
        self._icy_handle.mount = self.mount
        self._icy_handle.port = self.port
        self._icy_handle.open()

    def disconnect(self):
        IceProvider.LOG.info('disconnecting from icecast server.')
        try:
            self._icy_handle.sync()
            self._icy_handle.close()
        except Exception:
            IceProvider.LOG.log(logging.WARNING,
                    'Error disconnecting from icecast.',
                    exc_info=True)

    def listener_ips(self):
        """
        Scrape the Icecast admin page for current listeners and return a list
        of MD5 hashes of their IPs
        """

        if not all((self.admin_url, self.admin_username, self.admin_password)):
            # not all required backend parameters supplied
            LOG.warning("Not all parameters set for screen scraping icecast "
                    "statistics. Need admin-url, user and password")
            return

        int_octet = "25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]?"
        p = re.compile(r"(((%s)\.){3}(%s))" % (int_octet, int_octet))

        # Create an URL opener with support for Basic HTTP Authentication...
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='Icecast2 Server',
                                  uri=self.admin_url,
                                  user=self.admin_username,
                                  passwd=self.admin_password)
        opener = urllib2.build_opener(auth_handler)
        # ...and install it globally so it can be used with urlopen.
        urllib2.install_opener(opener)

        try:
            LOG.debug("Opening %r" % self.admin_url)
            handler = urllib2.urlopen(self.admin_url)
            data = handler.read()

            listeners = [x[0] for x in p.findall(data)]
            return listeners
        except urllib2.HTTPError, ex:
            LOG.error("Error opening %r: Caught %s" % (
                self.admin_url, ex))
            return []
        except urllib2.URLError, ex:
            LOG.error("Error opening %r: Caught %s" % (
                self.admin_url, ex))
            return []

    def run(self):
        while True:
            chunk = self.qin.get()
            self._icy_handle.send(chunk)
            self._icy_handle.sync()


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('__main__.FileReader').setLevel(logging.INFO)
    logging.getLogger('__main__.Player').setLevel(logging.INFO)
    logging.getLogger('__main__.IceProvider').setLevel(logging.INFO)

    sys.path.insert(0, os.getcwd())
    if len(sys.argv) < 2:
        print """
        USAGE: %s <filename>
        """ % sys.argv[0]
        sys.exit(1)

    icy_conf = {
        'port': 8001,
        'mount': "/wicked.mp3",
        'pwd': "mussdulauschtren"}

    channel_id = 1
    player = Player(channel_id, icy_conf)
    player.queue(sys.argv[1])
    player.start()

    time.sleep(0.1)
    player.pause()
    time.sleep(0.1)
    player.pause()
    time.sleep(0.1)
    player.stop()
    time.sleep(0.1)
