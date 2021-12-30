# type: ignore
import _thread
import os
import sys

import glib
import gobject
import pygst

pygst.require("0.10")
import time

import gst

PLAYER = None
IS_PLAYING = False


def on_message(bus, message):
    global IS_PLAYING
    if message.type == gst.MESSAGE_EOS:
        print("EOS reached")
        PLAYER.set_state(gst.STATE_NULL)
        IS_PLAYING = False
    elif message.type == gst.MESSAGE_ERROR:
        PLAYER.set_state(gst.STATE_NULL)
        err, debug = message.parse_error()
        print("Error: %s" % err)
        print("Debug info: %s" % debug)
        IS_PLAYING = False
    else:
        print(message)


def play(filename):
    global IS_PLAYING
    if not os.path.isfile(filename):
        print("%r is not a file!" % filename)
        return

    IS_PLAYING = True
    PLAYER.get_by_name("file-source").set_property("location", filename)
    PLAYER.set_state(gst.STATE_PLAYING)
    while IS_PLAYING:
        time.sleep(1)
    LOOP.quit()


def init_player():
    global PLAYER
    PLAYER = gst.Pipeline("player")
    source = gst.element_factory_make("filesrc", "file-source")
    decoder = gst.element_factory_make("mad", "mp3-decoder")
    conv = gst.element_factory_make("audioconvert", "converter")
    sink = gst.element_factory_make("alsasink", "alsa-output")
    PLAYER.add(source, decoder, conv, sink)
    gst.element_link_many(source, decoder, conv, sink)
    bus = PLAYER.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message)


if __name__ == "__main__":
    init_player()
    _thread.start_new_thread(play, (sys.argv[1],))
    gobject.threads_init()
    LOOP = glib.MainLoop()
    LOOP.run()
