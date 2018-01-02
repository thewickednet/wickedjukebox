from threading import Thread
from time import sleep
import logging
import os
import sys

import gi

LOG = logging.getLogger(__name__)

os.environ["GST_DEBUG_DUMP_DOT_DIR"] = "/tmp"
os.putenv('GST_DEBUG_DUMP_DIR_DIR', '/tmp')

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject  # NOQA


def bus_call(bus, message, loop):
    if message.type == Gst.MessageType.EOS:
        LOG.debug('End of Stream')
        loop.quit()
    elif message.type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        LOG.error('!! Error %s: %s', err, debug)
        loop.quit()
    return True


filename2 = sys.argv[2]


audioconvert = Gst.ElementFactory.make('audioconvert')
def pad_added(src, pad):
    target = audioconvert.sinkpads[0]
    pad_name = '%s:%s' % (pad.get_parent_element().name, pad.name)
    tgt_name = '%s:%s' % (target.get_parent_element().name, target.name)
    LOG.debug('Pad %s added to %s', pad_name, src.name)
    LOG.debug('   Linking %s to %s', pad_name, tgt_name)
    pad.link(target)


pipeline = Gst.Pipeline('mypipeline')
# XXX filesrc = Gst.ElementFactory.make('filesrc')
# XXX filesrc.set_property('location', sys.argv[1])
# XXX decodebin = Gst.ElementFactory.make('decodebin')
# XXX decodebin.connect('pad-added', pad_added)
# XXX audioresample = Gst.ElementFactory.make('audioresample')
# XXX alsasink = Gst.ElementFactory.make('alsasink')
# XXX # shout = Gst.ElementFactory.make('shout2send')
# XXX
# XXX pipeline.add(filesrc)
# XXX pipeline.add(decodebin)
# XXX pipeline.add(audioconvert)
# XXX pipeline.add(audioresample)
# XXX pipeline.add(alsasink)
# XXX # pipeline.add(shout)
# XXX
# XXX filesrc.link(decodebin)
# XXX audioconvert.link(audioresample)
# XXX audioresample.link(alsasink)
# XXX # audioresample.link(shout)
# XXX
# XXX GObject.threads_init()
# XXX Gst.init(None)
# XXX
# XXX loop = GObject.MainLoop()
# XXX bus = pipeline.get_bus()
# XXX bus.add_signal_watch()
# XXX bus.connect('message', bus_call, loop)
# XXX
# XXX Gst.debug_bin_to_dot_file(
# XXX     pipeline,
# XXX     Gst.DebugGraphDetails.ALL,
# XXX     'supersimple-debug-graph')
# XXX
# XXX pipeline.set_state(Gst.State.PLAYING)
# XXX try:
# XXX     loop.run()
# XXX except Exception:
# XXX     LOG.exception('Exception raised during main loop')
# XXX
# XXX pipeline.set_state(Gst.State.NULL)
