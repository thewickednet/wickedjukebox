import logging
import os

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject  # NOQA

LOG = logging.getLogger(__name__)


def bus_call(bus, message, loop):
    if message.type == Gst.MessageType.EOS:
        LOG.debug('End of Stream')
        loop.quit()
    elif message.type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        LOG.error('!! Error %s: Debug INFO: %s', err, debug)
        loop.quit()
    elif message.type == Gst.MessageType.STATE_CHANGED:
        old, new, pending = message.parse_state_changed()
        LOG.debug('State changed from %s to %s (pending=%s)',
                  old.value_name, new.value_name, pending.value_name)
    elif message.type == Gst.MessageType.STREAM_STATUS:
        type_, owner = message.parse_stream_status()
        LOG.debug('Stream status changed to %s (owner=%s)',
                  type_.value_name, owner.name)
    elif message.type == Gst.MessageType.DURATION_CHANGED:
        LOG.debug('Duration changed')
    else:
        LOG.debug('!! Unknown message type: %r', message.type)
    return True


def pad_factory(element):
    def pad_added(src, pad):
        target = element.sinkpads[0]
        pad_name = '%s:%s' % (pad.get_parent_element().name, pad.name)
        tgt_name = '%s:%s' % (target.get_parent_element().name, target.name)
        LOG.debug('New dynamic pad %s detected on %s. Auto-linking it to %s',
                  pad_name, src.name, tgt_name)
        pad.link(target)
    return pad_added


def debug_event(*args, **kwargs):
    LOG.debug('Debug Event: %r, %r', args, kwargs)


def play(filename):
    LOG.info('Playing %r', filename)
    Gst.init(None)

    pipeline = Gst.Pipeline()

    # Create pipeline elements
    filesrc = Gst.ElementFactory.make('filesrc')
    filesrc.set_property('location', filename)
    audioconvert = Gst.ElementFactory.make('audioconvert')
    decodebin = Gst.ElementFactory.make('decodebin')
    decodebin.connect('pad-added', pad_factory(audioconvert))
    audioresample = Gst.ElementFactory.make('audioresample')
    audioresample.connect('pad-added', debug_event)
    shout = Gst.ElementFactory.make('shout2send')
    shout.set_property('mount', "/stream.mp3")
    shout.set_property('port', 8001)
    shout.set_property('username', "stream")
    shout.set_property('password', "supersecret")
    shout.connect('connection-problem', debug_event)

    # Add elements to pipeline
    pipeline.add(filesrc)
    pipeline.add(decodebin)
    pipeline.add(audioconvert)
    pipeline.add(audioresample)
    pipeline.add(shout)

    # Link pipeline
    filesrc.link(decodebin)
    # decodebing is dynamically linked to audioconvert by pad_factory
    audioconvert.link(audioresample)
    audioresample.link(shout)

    bus = pipeline.get_bus()
    bus.add_signal_watch()

    # Start playback
    GObject.threads_init()
    loop = GObject.MainLoop()
    bus.connect('message', bus_call, loop)

    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except Exception:
        LOG.exception('Exception raised during main loop')
    LOG.info('Finished playback, cleaning up')
    pipeline.set_state(Gst.State.NULL)

    Gst.debug_bin_to_dot_file(
        pipeline,
        Gst.DebugGraphDetails.ALL,
        'supersimple-debug-graph')

    # XXX pipeline = (
    # XXX     'filesrc location="{filename}" ! '
    # XXX     'decodebin ! '
    # XXX     'audioconvert ! '
    # XXX     'vorbisenc ! '
    # XXX     'oggmux ! '
    # XXX     'shout2send mount="{mount}" port={port} '
    # XXX     'username={user} password={passwd}')
    # XXX player = gst.parse_launch(pipeline.format(
    # XXX         filename=filename,
    # XXX         mount="/bla.ogg",
    # XXX         port="8000",
    # XXX         user="source",
    # XXX         passwd="test123"
    # XXX     ))


try:
    from gouge.colourcli import Simple
    Simple.basicConfig(level=0)
except ImportError:
    import logging
    logging.basicConfig(level=0)

os.environ["GST_DEBUG_DUMP_DOT_DIR"] = "/tmp"
os.putenv('GST_DEBUG_DUMP_DIR_DIR', '/tmp')
os.putenv('GST_DEBUG', '3')
play('/var/mp3/Tagged/The Pretty Reckless/Who You Selling For/02 Oh My God.mp3')
