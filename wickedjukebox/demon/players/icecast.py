# TODO: Maybe it would be better to have a "global" atexit function properly
# TODO:    supervising stopping the threads.
from __future__ import print_function

import atexit
import logging
import os
import re
import time
from Queue import Empty, Full, Queue
from threading import Thread

import requests
from pkg_resources import resource_stream

import shout
from common import STATUS_PAUSED, STATUS_STOPPED

LOG = logging.getLogger(__name__)

SCMD_QUEUE = 'queue'
SCMD_PAUSE = 'pause'
SCMD_SKIP = 'skip'
SCMD_START = 'start'
SCMD_STOP = 'stop'

ICMD_SET_TITLE = 'set_title'


class Player(object):

    LOG = logging.getLogger('{0}.Player'.format(__name__))

    def __init__(self, channel_id, icy_conf):
        Player.LOG.debug('Initialising with %r, %r', channel_id, icy_conf)
        self.source_command = Queue()
        dataq = Queue(16)
        icy_commands = Queue(1)
        self.filereader = FileReader(self.source_command, dataq, icy_commands)
        self.provider = IceProvider(dataq, icy_commands, icy_conf)
        self.filereader.start()
        self.provider.start()

    def crop_playlist(self, max_items=2):
        Player.LOG.debug('Cropping playlist to %s items', max_items)
        self.filereader.crop_queue(max_items)

    def listeners(self):
        return self.provider.listener_ips()

    def position(self):
        Player.LOG.debug('Interpreting position %r',
                         self.filereader.position())
        try:
            a, b = self.filereader.position()
            return float(a) / float(b) * 100
        except ZeroDivisionError:
            return 0.0

    def current_song(self):
        if not self.filereader.current_file:
            return ''
        return self.filereader.current_file.name

    def pause(self):
        self.source_command.put((SCMD_PAUSE, None))

    def queue(self, song):
        self.source_command.put((SCMD_QUEUE, song))

    def skip(self):
        self.source_command.put((SCMD_SKIP, None))

    def start(self):
        self.source_command.put((SCMD_START, None))

    def status(self):
        return self.filereader.status

    def stop(self):
        self.source_command.put((SCMD_STOP, None))

    @property
    def queuesize(self):
        return len(self.filereader.song_queue)


class FileReader(Thread):

    LOG = logging.getLogger('{0}.FileReader'.format(__name__))

    def __init__(self, qcmds, qdata, icy_commands, *args, **kwargs):
        FileReader.LOG.debug('Initialising with %r, %r, %r, %r',
                             qcmds, qdata, args, kwargs)
        super(FileReader, self).__init__(*args, **kwargs)
        self.qcmds = qcmds
        self._icy_commands = icy_commands
        self.qdata = qdata
        self.daemon = True
        self.current_file = None
        self._stat = None
        self.chunk_size = 1024
        self.status = STATUS_STOPPED
        self.__noisefile = resource_stream('wickedjukebox',
                                           'resources/noise.mp3')
        self.song_queue = []

    def run(self):
        FileReader.LOG.debug('Starting')
        do_skip = False
        while True:
            try:
                cmd, args = self.qcmds.get(False)
                FileReader.LOG.debug('Recieved command %r with args %r',
                                     cmd, args)
                if cmd == SCMD_QUEUE:
                    self.song_queue.append(args)
                    FileReader.LOG.info('Queueing %r. Queue is now: %r',
                                        args, self.song_queue)
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
                self.qcmds.task_done()
            except Empty:
                pass

            if do_skip and self.song_queue:
                FileReader.LOG.debug('Skip requested on queue %r',
                                     self.song_queue)
                new_song = self.song_queue.pop(0)
                self.closefile()
                self.openfile(new_song['filename'])
                self._set_title(new_song)
                FileReader.LOG.debug('Previous file closed and reopened '
                                     'with %r. Queue is now: %r',
                                     new_song['filename'],
                                     self.song_queue)
                do_skip = False

            if not self.current_file and self.song_queue:
                FileReader.LOG.debug('No file currently open, but we have '
                                     'a queue: %r. Opening...',
                                     self.song_queue)
                new_song = self.song_queue.pop(0)
                self._set_title(new_song)
                self.openfile(new_song['filename'])

            send_noise = False
            chunk = ''
            if self.status in (STATUS_STOPPED, STATUS_PAUSED):
                send_noise = True
            else:
                if self.current_file:
                    chunk = self.current_file.read(self.chunk_size)
                    if chunk:
                        send_noise = False
                    else:
                        self.closefile()
                        send_noise = True
                else:
                    send_noise = True

            if send_noise:
                self.qdata.put(self.__get_noise())
            else:
                self.qdata.put(chunk)

    def __get_noise(self):
        output = self.__noisefile.read(self.chunk_size)
        if not output:
            self.__noisefile.seek(0)
            output = self.__noisefile.read(self.chunk_size)
        return output

    def _set_title(self, song):
        """
        Sets the title on the icecast provider
        """
        try:
            title = u'{0[artist]} - {0[title]}'.format(song)
            FileReader.LOG.debug(u'Telling IceProvider to set new title '
                                 u'to %s', title)
            self._icy_commands.put_nowait((ICMD_SET_TITLE,
                                           title.encode('utf8')))
        except Full:
            pass

    def closefile(self):
        FileReader.LOG.debug('Closing %r', self.current_file)
        self.current_file.close()
        self.current_file = None
        self._stat = None

    def openfile(self, fname):
        FileReader.LOG.debug('Opening %r', fname)
        self.current_file = open(fname, 'rb')
        self._stat = os.stat(fname)

    def position(self):
        if not self.current_file and not self.song_queue:
            # no file opened, and queue empty. Send a nearly finished progress
            # as finished. This will cause the jukebox channel to send a new
            # song to the queue.
            return (99, 100)

        if self.current_file and self._stat:
            return (self.current_file.tell(), self._stat.st_size)
        else:
            return (0, 0)

    def crop_queue(self, max_items):
        # TODO: implement
        pass


class IceProvider(Thread):

    LOG = logging.getLogger('{0}.IceProvider'.format(__name__))

    def __init__(self, data_queue, cmd_queue, params, *args, **kwargs):
        super(IceProvider, self).__init__(*args, **kwargs)
        self.data_queue = data_queue
        self.cmd_queue = cmd_queue
        self.daemon = True
        IceProvider.LOG.info("connection to icecast server (params = %s)",
                             params)
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
            self.admin_username = params["admin_username"]

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
            IceProvider.LOG.warning(
                'Error disconnecting from icecast.',
                exc_info=True)

    def listener_ips(self):
        """
        Scrape the Icecast admin page for current listeners and return a list
        of MD5 hashes of their IPs
        """

        if not all((self.admin_url, self.admin_username, self.admin_password)):
            # not all required backend parameters supplied
            IceProvider.LOG.warning("Not all parameters set for screen "
                                    "scraping icecast statistics. Need "
                                    "admin-url, user and password")
            return []

        int_octet = "25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9]?"
        p = re.compile(r"(((%s)\.){3}(%s))" % (int_octet, int_octet))

        IceProvider.LOG.debug("Opening %r", self.admin_url)
        response = requests.get(self.admin_url, auth=(self.admin_username,
                                                      self.admin_password))
        if response.status_code == 200:
            listeners = [x[0] for x in p.findall(response.text)]
            IceProvider.LOG.debug('Current listeners: %r', listeners)
            return listeners
        else:
            IceProvider.LOG.error(
                "Error opening %r: Status: %s: %s",
                self.admin_url, response.status_code, response.text)
            return []

    def run(self):
        while True:
            chunk = self.data_queue.get()
            try:
                cmd, args = self.cmd_queue.get(False)
                if cmd == ICMD_SET_TITLE:
                    IceProvider.LOG.debug('Setting title to %r', args)
                    self._icy_handle.set_metadata({'song': args})
                self.cmd_queue.task_done()
            except Empty:
                pass
            self._icy_handle.send(chunk)
            self._icy_handle.sync()
            self.data_queue.task_done()


def main():
    import sys

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('__main__.FileReader').setLevel(logging.INFO)
    logging.getLogger('__main__.Player').setLevel(logging.INFO)
    logging.getLogger('__main__.IceProvider').setLevel(logging.INFO)

    sys.path.insert(0, os.getcwd())
    if len(sys.argv) < 2:
        print("""
        USAGE: %s <filename>
        """ % sys.argv[0])
        sys.exit(1)

    icy_conf = {
        'port': 8001,
        'mount': "/wicked.mp3",
        'pwd': "mussdulauschtren"}

    testsong = {
        'filename': sys.argv[1],
        'artist': 'theartistname',
        'title': 'thetitle'}

    channel_id = 1
    player = Player(channel_id, icy_conf)
    player.queue(testsong)
    player.start()

    time.sleep(1)
    player.pause()
    time.sleep(20)
    player.pause()
    time.sleep(30)


if __name__ == "__main__":
    main()
