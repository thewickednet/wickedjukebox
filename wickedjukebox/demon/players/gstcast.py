import re
from datetime import datetime
from threading import Thread
import logging
import urllib.request, urllib.error, urllib.parse
from hashlib import md5

import gi
from gi.repository import Gst, GObject

from wickedjukebox.demon.dbmodel import State


gi.require_version('Gst', '1.0')
LOG = logging.getLogger(__name__)


class PlayerState(object):
    def __init__(self):
        self.song_started = None
        self.admin_password = None
        self.admin_url = None
        self.admin_user = None
        self.channel_id = 0
        self.mount = None
        self.password = None
        self.port = None
        self.queue = []
        self.server = None


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
        self.pipeline = gst.Pipeline("player")

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


def init():
    LOG.info("Initialising gstreamer player")


def release():
    LOG.info("Releasing gstreamer player resources")


def config(params):
    LOG.info("GStreamer client initialised with params %s" % params)
    STATE.port = int(params['port'])
    STATE.mount = str(params['mount'])
    STATE.password = str(params['pwd'])
    STATE.channel_id = int(params['channel_id'])

    if "admin_url" in params:
        STATE.admin_url = (str(params["admin_url"]) +
               "/listclients.xsl?mount=" +
               STATE.mount)

    if "admin_username" in params:
        STATE.admin_username = str(params["admin_username"])

    if "admin_password" in params:
        STATE.admin_password = str(params["admin_password"])


def getPosition():
    if not STATE.server:
        output = (0, 100)
    else:
        output = STATE.server.current_position()
    State.set("progress", output[0], STATE.channel_id)
    return output


def getSong():
    if STATE.server:
        return STATE.server.filename
    return None


def queue(filename):
    from wickedjukebox.demon.dbmodel import Setting
    LOG.debug("Received a queue (%s)" % filename)
    if Setting.get('sys_utctime', 0) == 0:
        STATE.song_started = datetime.utcnow()
    else:
        STATE.song_started = datetime.now()

    STATE.queue.append(filename)


def cropPlaylist(length=2):
    """
    Removes items from the *beginning* of the playlist to ensure it has only
    a fixed number of entries.

    @type  length: int
    @param length: The new size of the playlist
    """
    LOG.debug("Cropping pl to %d songs" % length)
    if len(STATE.queue) <= length:
        return True

    STATE.queue = STATE.queue[-length:]
    return True


def skipSong():
    LOG.debug("Received a skip request")
    stopPlayback()
    startPlayback()


def stopPlayback():
    from wickedjukebox.demon.dbmodel import State

    LOG.debug("Stopping playback")
    if STATE.server:
        STATE.server.stop()

    State.set("progress", 0, STATE.channel_id)
    LOG.debug("Playback stopped")


def pausePlayback():
    pass


def startPlayback():
    from wickedjukebox.demon.dbmodel import State

    LOG.info("Starting playback")
    State.set("progress", 0, STATE.channel_id)
    if not STATE.queue:
        LOG.warn("Nothing on queue.")
        return False

    if not STATE.server:
        LOG.warn("No icecast connection available!")
        STATE.server = GStreamer()

    STATE.server.start_stop(STATE.queue.pop(0))


def status():
    if STATE.server:
        return STATE.server.status()
    else:
        return "stopped"


def current_listeners():
    """
    Scrape the Icecast admin page for current listeners and return a list of
    MD5 hashes of their IPs
    """

    if STATE.admin_url is None or \
        STATE.admin_username is None or \
        STATE.admin_password is None:
        # not all required backend parameters supplied
        LOG.warning("Not all parameters set for screen scraping icecast "
                "statistics. Need admin-url and admin-password")
        return

    part = "25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]?"
    p = re.compile(r"(((%s)\.){3}(%s))" % (part, part))

    # Create an OpenerDirector with support for Basic HTTP Authentication...
    auth_handler = urllib.request.HTTPBasicAuthHandler()
    auth_handler.add_password(realm='Icecast2 Server',
                              uri=STATE.admin_url,
                              user=STATE.admin_username,
                              passwd=STATE.admin_password)
    opener = urllib.request.build_opener(auth_handler)
    # ...and install it globally so it can be used with urlopen.
    urllib.request.install_opener(opener)

    try:
        LOG.debug("Opening %r" % STATE.admin_url)
        handler = urllib.request.urlopen(STATE.admin_url)
        data = handler.read()

        listeners = [md5(x[0]).hexdigest() for x in p.findall(data)]
        return listeners
    except urllib.error.HTTPError as ex:
        LOG.error("Error opening %r: Caught %r" % (STATE.admin_url, str(ex)))
        return None
    except urllib.error.URLError as ex:
        LOG.error("Error opening %r: Caught %r" % (STATE.admin_url, str(ex)))
        return None


STATE = PlayerState()
