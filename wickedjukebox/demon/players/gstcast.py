# XXX import re
from datetime import datetime
from threading import Thread
import logging
# XXX import urllib.request, urllib.error, urllib.parse
# XXX from hashlib import md5

import gi
gi.require_version('Gst', '1.0')  # This must come before importing Gst

from gi.repository import Gst, GObject

from wickedjukebox.demon.dbmodel import State


LOG = logging.getLogger(__name__)


class GStreamer(Thread):

    def decodebin_pad_added(self, src, pad):
        target = self.audioconvert.sinkpads[0]
        pad_name = '%s:%s' % (pad.get_parent_element().name, pad.name)
        tgt_name = '%s:%s' % (target.get_parent_element().name, target.name)
        LOG.debug('Pad %s added to %s', pad_name, src.name)
        LOG.debug('   Linking %s to %s', pad_name, tgt_name)
        pad.link(target)

    def __init__(self, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.daemon = True

        self.keep_running = True
        self.pipeline = None
        self.filename = None
        self.is_playing = False
        self.method = "module_method"
        LOG.info("GStreamer class initialised")
        self.init_player()

    def init_player(self):
        LOG.debug("Initialising the player thread")
        self.pipeline = Gst.Pipeline("player")

        self.filesrc = Gst.ElementFactory.make('filesrc')
        self.filesrc.set_property('location', filename)
        self.audioconvert = Gst.ElementFactory.make('audioconvert')
        decodebin = Gst.ElementFactory.make('decodebin')
        decodebin.connect('pad-added', self.decodebin_pad_added)
        audioresample = Gst.ElementFactory.make('audioresample')
        shout2send = Gst.ElementFactory.make('shout2send')

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

        self.pipeline.add(
            self.filesrc,
            decodebin,
            self.audioconvert,
            audioresample,
            shout2send,
        )

        self.filesrc.link(decodebin)
        self.audioconvert.link(audioresample)
        audioresample.link(shout2send)

    def current_position(self):
        try:
            return (int(self.pipeline.query_position(
                        Gst.Format.Time, None)[0] * 1E-9),
                    int(self.pipeline.query_duration(
                        Gst.Format.Time, None)[0] * 1E-9))
        except Exception as exc:
            LOG.error(exc)
            return (0, 100)

    def on_message(self, bus, message, loop):
        """
        gstramer callback.

        gstreamer calls this method from time to time sending additional
        payload along the "message" parameter
        """
        if message.type == Gst.MessageType.EOS:
            LOG.debug('End of Stream')
            loop.quit()
            self.pipeline.set_state(Gst.State.READY)
            self.is_playing = False
        elif message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            LOG.error('!! Error %s: %s', err, debug)
            loop.quit()
            self.pipeline.set_state(Gst.State.READY)
            self.is_playing = False
        return True

    def stop(self):
        LOG.info("Stopping stream")
        self.filename = None
        self.pipeline.set_state(Gst.State.READY)
        self.is_playing = False
        self.keep_running = False

    def status(self):
        return self.is_playing and "playing" or "stop"

    def play(self, filename):
        if not self.keep_running:
            LOG.warning("Thread has been stopped! Will not play this file!")
            return
        self.filename = filename

    def set_file(self, new_filename):
        """
        Start playing a different file
        """
        self.pipeline.set_state(Gst.State.READY)
        self.filesrc.set_property('location', new_filename)
        self.pipeline.set_state(Gst.State.PLAYING)

    def run(self):
        LOG.debug("GStreamer player thread started")
        # XXX self.pipeline.get_by_name("encoder").set_property("bitrate", 128)
        # XXX self.pipeline.get_by_name("tagger").set_property(
        # XXX     "tags", "album=testalbum,title=testtitle,artist=testartist")
        self.pipeline.get_by_name("shout2send").set_property("ip", "127.0.0.1")
        self.pipeline.get_by_name("shout2send").set_property("port", STATE.port)
        self.pipeline.get_by_name("shout2send").set_property(
            "password", STATE.password)
        self.pipeline.get_by_name("shout2send").set_property(
            "mount", STATE.mount)
        self.pipeline.get_by_name("shout2send").set_property(
            "streamname", "The Wicked Jukebox - test.mp3")

        loop = GObject.MainLoop()

        self.pipeline.get_by_name("filesrc").set_property(
            "location",
            self.filename)
        self.is_playing = True
        self.pipeline.set_state(Gst.State.PLAYING)
        try:
            loop.run()
        except Exception:
            LOG.exception('Exception raised during main loop')

        LOG.debug("GStreamer player thread stopped")



STREAMER = GStreamer()

def init():
    LOG.info("Initialising gstreamer player")
    STREAMER.start()


def release():
    LOG.info("Releasing gstreamer player resources")
    STREAMER.stop()
    STREAMER.join()


def config(params):
    LOG.info("GStreamer client initialised with params %s" % params)
    STREAMER.port = int(params['port'])
    STREAMER.mount = str(params['mount'])
    STREAMER.password = str(params['pwd'])
    STREAMER.channel_id = int(params['channel_id'])

    if "admin_url" in params:
        STREAMER.admin_url = (str(params["admin_url"]) +
               "/listclients.xsl?mount=" +
               STREAMER.mount)

    if "admin_username" in params:
        STREAMER.admin_username = str(params["admin_username"])

    if "admin_password" in params:
        STREAMER.admin_password = str(params["admin_password"])


def getPosition():
    # TODO
    output (0, 100)
    State.set("progress", output[0], STREAMER.channel_id)
    return output


def getSong():
    return STREAMER.current_filename


def queue(filename):
    from wickedjukebox.demon.dbmodel import Setting
    LOG.debug("Received a queue (%s)" % filename)
    if Setting.get('sys_utctime', 0) == 0:
        STREAMER.song_started = datetime.utcnow()
    else:
        STREAMER.song_started = datetime.now()

    STREAMER.queue(filename)


def cropPlaylist(length=2):
    """
    Removes items from the *beginning* of the playlist to ensure it has only
    a fixed number of entries.

    @type  length: int
    @param length: The new size of the playlist
    """
    LOG.debug("Cropping pl to %d songs" % length)
    STREAMER.crop_playlist(length)
    return True


def skipSong():
    LOG.debug("Received a skip request")
    stopPlayback()
    startPlayback()


def stopPlayback():
    from wickedjukebox.demon.dbmodel import State

    LOG.debug("Stopping playback")
    STREAMER.stop()

    State.set("progress", 0, STREAMER.channel_id)
    LOG.debug("Playback stopped")


def pausePlayback():
    LOG.debug("Pausing playback")
    STREAMER.pause()
    LOG.debug("Playback paused")


def startPlayback():
    from wickedjukebox.demon.dbmodel import State

    LOG.info("Starting playback")
    State.set("progress", 0, STREAMER.channel_id)
    STREAMER.play()


def status():
    return STREAMER.status()


def current_listeners():
    """
    Scrape the Icecast admin page for current listeners and return a list of
    MD5 hashes of their IPs
    """
    return []  # TODO

    # XXX if STATE.admin_url is None or \
    # XXX     STATE.admin_username is None or \
    # XXX     STATE.admin_password is None:
    # XXX     # not all required backend parameters supplied
    # XXX     LOG.warning("Not all parameters set for screen scraping icecast "
    # XXX             "statistics. Need admin-url and admin-password")
    # XXX     return

    # XXX part = "25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]?"
    # XXX p = re.compile(r"(((%s)\.){3}(%s))" % (part, part))

    # XXX # Create an OpenerDirector with support for Basic HTTP Authentication...
    # XXX auth_handler = urllib.request.HTTPBasicAuthHandler()
    # XXX auth_handler.add_password(realm='Icecast2 Server',
    # XXX                           uri=STATE.admin_url,
    # XXX                           user=STATE.admin_username,
    # XXX                           passwd=STATE.admin_password)
    # XXX opener = urllib.request.build_opener(auth_handler)
    # XXX # ...and install it globally so it can be used with urlopen.
    # XXX urllib.request.install_opener(opener)

    # XXX try:
    # XXX     LOG.debug("Opening %r" % STATE.admin_url)
    # XXX     handler = urllib.request.urlopen(STATE.admin_url)
    # XXX     data = handler.read()

    # XXX     listeners = [md5(x[0]).hexdigest() for x in p.findall(data)]
    # XXX     return listeners
    # XXX except urllib.error.HTTPError as ex:
    # XXX     LOG.error("Error opening %r: Caught %r" % (STATE.admin_url, str(ex)))
    # XXX     return None
    # XXX except urllib.error.URLError as ex:
    # XXX     LOG.error("Error opening %r: Caught %r" % (STATE.admin_url, str(ex)))
    # XXX     return None
