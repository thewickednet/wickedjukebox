"""
Entry points, and helpers for the command line interface.
"""

import signal
import time
import logging
from pydata.channel import Channel
from pydata import setup_logging
setup_logging()
logger = logging.getLogger(__name__)
CHANNEL = None
KEEP_RUNNING = True


def handle_sigint(signal, frame):
    """
    Try to exit cleanly on SIGINT.
    """
    global KEEP_RUNNING, CHANNEL
    logging.info("SIGINT caught")
    CHANNEL.close()
    KEEP_RUNNING = False


def run_channel(channel_name):
    """
    Starts a channel
    """
    global CHANNEL

    while KEEP_RUNNING:
        CHANNEL = Channel(channel_name)
        try:
            logging.info("Starting channel %s" % channel_name)
            CHANNEL.startPlayback()
            CHANNEL.run()
        except Exception:
            import traceback
            logging.critical(traceback.format_exc())
            logging.info("Restarting channel %s" % channel_name)
            CHANNEL.close()
            CHANNEL = None
            CHANNEL = Channel(channel_name)

        if CHANNEL:
            logging.info("Closing channel")
            CHANNEL.close()

        time.sleep(1)


def main():
    """
    Parse command line options, bootstrap the app and run the channel
    """
    from optparse import OptionParser
    signal.signal(signal.SIGINT, handle_sigint)

    parser = OptionParser()
    parser.add_option("-c", "--channel", dest="channel_name",
        help="runs the channel named CHANNEL_NAME", metavar="CHANNEL_NAME")
    parser.add_option("-v", action="count", dest="verbosity",
            help=("Application verbosity. Can be repeated up to 5 times, each "
                  "time increasing verbosity). If not set, the logging "
                  "configuration file will take precedence."))

    (options, args) = parser.parse_args()

    if not options.channel_name:
        parser.error("CHANNEL_NAME is required!")

    verbosity_map = {
            5: logging.DEBUG,
            4: logging.INFO,
            3: logging.WARN,
            2: logging.ERROR,
            1: logging.CRITICAL,
            }
    if options.verbosity and options.verbosity in verbosity_map:
        logger.setLevel(verbosity_map[options.verbosity])
    elif options.verbosity and options.verbosity > len(verbosity_map):
        logger.setLevel(logging.DEBUG)

    run_channel(options.channel_name)
