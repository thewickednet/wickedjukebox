import pygst

pygst.require("0.10")
import logging

import glib
import gobject
import gst

LOG = logging.getLogger(__name__)


def play(filename):
    loop = None
    player = None

    def on_message(bus, message):
        if message.type == gst.MESSAGE_EOS:
            LOG.debug("EOS reached")
            player.set_state(gst.STATE_NULL)
            loop.quit()
        elif message.type == gst.MESSAGE_ERROR:
            player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            LOG.error("Error: %s" % err)
            LOG.debug("Debug info: %s" % debug)
            loop.quit()

    pipeline = (
        'filesrc location="{filename}" ! '
        'decodebin ! '
        'audioconvert ! '
        'vorbisenc ! '
        'oggmux ! '
        'shout2send '
        'mount="{mount}" '
        'port={port} '
        'username={user} '
        'password={passwd}'
    )
    player = gst.parse_launch(
        pipeline.format(
            filename=filename,
            mount="/bla.ogg",
            port="8000",
            user="source",
            passwd="test123",
        )
    )

    bus = player.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message)

    player.set_state(gst.STATE_PLAYING)

    gobject.threads_init()
    loop = glib.MainLoop()
    loop.run()
