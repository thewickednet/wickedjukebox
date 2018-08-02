"""
Entry points, and helpers for the command line interface.
"""
import logging
import signal
import time
from argparse import ArgumentParser

from wickedjukebox import __version__, setup_logging
from wickedjukebox.core.channel import Channel

LOG = logging.getLogger(__name__)


class Application(object):

    def __init__(self):
        self.channel = None
        self.keep_running = True

    def handle_sigint(self, signal_num, frame):  # pylint: disable=unused-argument
        """
        Try to exit cleanly on SIGINT.
        """
        LOG.info("SIGINT caught")
        self.channel.close()
        self.keep_running = False

    def run_channel(self, channel_name):
        """
        Starts a channel
        """

        while self.keep_running:
            self.channel = Channel(channel_name)
            try:
                LOG.info("Starting channel %s", channel_name)
                self.channel.startPlayback()
                self.channel.run()
            except Exception:  # pylint: disable=broad-except
                # We allow "broad-except" here. This is a
                # "shit-has-hit-the-fan" code. Trying to restart the channel
                # might resolve the issue.
                LOG.exception('Unhandled exception, trying to restart channel')
                LOG.info("Restarting channel %s", channel_name)
                self.channel.close()
                self.channel = None
                self.channel = Channel(channel_name)

            if self.channel:
                LOG.info("Closing channel")
                self.channel.close()

            time.sleep(1)


def main():
    """
    Parse command line options, bootstrap the app and run the channel
    """
    setup_logging()

    LOG.info(" Wicked Jukebox %s", __version__.center(79, '#'))

    parser = ArgumentParser()
    parser.add_argument("-c", "--channel", dest="channel_name",
                        help="runs the channel named CHANNEL_NAME",
                        metavar="CHANNEL_NAME")
    parser.add_argument("-v", action="count", dest="verbosity",
                        help=("Application verbosity. Can be repeated up to 5 "
                              "times, each time increasing verbosity). If not "
                              "set, the logging configuration file will take "
                              "precedence."))

    args = parser.parse_args()

    if not args.channel_name:
        parser.error("CHANNEL_NAME is required!")

    verbosity_map = {
        5: logging.DEBUG,
        4: logging.INFO,
        3: logging.WARN,
        2: logging.ERROR,
        1: logging.CRITICAL,
    }
    if args.verbosity and args.verbosity in verbosity_map:
        LOG.setLevel(verbosity_map[args.verbosity])
    elif args.verbosity and args.verbosity > len(verbosity_map):
        LOG.setLevel(logging.DEBUG)

    app = Application()
    signal.signal(signal.SIGINT, app.handle_sigint)
    app.run_channel(args.channel_name)
