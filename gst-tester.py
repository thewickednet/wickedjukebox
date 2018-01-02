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


class Player(Thread):

    def pad_added(self, src, pad):
        target = self.audioconvert.sinkpads[0]
        pad_name = '%s:%s' % (pad.get_parent_element().name, pad.name)
        tgt_name = '%s:%s' % (target.get_parent_element().name, target.name)
        LOG.debug('Pad %s added to %s', pad_name, src.name)
        LOG.debug('   Linking %s to %s', pad_name, tgt_name)
        pad.link(target)

    def __init__(self, filename, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)
        self.daemon = True

        self.pipeline = Gst.Pipeline()

        self.filesrc = Gst.ElementFactory.make('filesrc')
        print('>>>', filename)
        self.filesrc.set_property('location', filename)
        self.audioconvert = Gst.ElementFactory.make('audioconvert')
        decodebin = Gst.ElementFactory.make('decodebin')
        decodebin.connect('pad-added', self.pad_added)
        audioresample = Gst.ElementFactory.make('audioresample')
        # alsasink = Gst.ElementFactory.make('alsasink')
        shout = Gst.ElementFactory.make('shout2send')

        self.pipeline.add(self.filesrc)
        self.pipeline.add(decodebin)
        self.pipeline.add(self.audioconvert)
        self.pipeline.add(audioresample)
        # self.pipeline.add(alsasink)
        self.pipeline.add(shout)

        self.filesrc.link(decodebin)
        self.audioconvert.link(audioresample)
        # audioresample.link(alsasink)
        audioresample.link(shout)

    def set_file(self, new_filename):
        self.pipeline.set_state(Gst.State.READY)
        self.filesrc.set_property('location', new_filename)
        self.pipeline.set_state(Gst.State.PLAYING)

    def run(self):
        loop = GObject.MainLoop()
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message', bus_call, loop)

        Gst.debug_bin_to_dot_file(
            self.pipeline,
            Gst.DebugGraphDetails.ALL,
            'supersimple-debug-graph')

        self.pipeline.set_state(Gst.State.PLAYING)
        try:
            loop.run()
        except Exception:
            LOG.exception('Exception raised during main loop')

        self.pipeline.set_state(Gst.State.NULL)


if __name__ == '__main__':

    GObject.threads_init()
    Gst.init(None)
    filename = '/var/mp3/Tagged/Carpenter Brut/Trilogy/Carpenter Brut - TRILOGY - 01 Escape From Midwich Valley.mp3'
    player = Player(filename)
    player.start()

    # XXX sleep(5)
    # XXX player.set_file(filename2)
    # XXX sleep(5)
