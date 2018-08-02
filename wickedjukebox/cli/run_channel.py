"""
Entry points, and helpers for the command line interface.
"""
import logging
import signal
import time

from wickedjukebox import __version__, setup_logging
from wickedjukebox.core.channel import Channel

LOG = logging.getLogger(__name__)


class Application(object):

    def __init__(self):
        self.channel = None
        self.keep_running = True

    def handle_sigint(self, signal, frame):
        """
        Try to exit cleanly on SIGINT.
        """
        logging.info("SIGINT caught")
        self.channel.close()
        self.keep_running = False

    def run_channel(self, channel_name):
        """
        Starts a channel
        """

        while self.keep_running:
            self.channel = Channel(channel_name)
            try:
                logging.info("Starting channel %s" % channel_name)
                self.channel.startPlayback()
                self.channel.run()
            except Exception:
                import traceback
                logging.critical(traceback.format_exc())
                logging.info("Restarting channel %s" % channel_name)
                self.channel.close()
                self.channel = None
                self.channel = Channel(channel_name)

            if self.channel:
                logging.info("Closing channel")
                self.channel.close()

            time.sleep(1)


def main():
    """
    Parse command line options, bootstrap the app and run the channel
    """
    from optparse import OptionParser
    setup_logging()

    LOG.info(" Wicked Jukebox {0} ".format(__version__).center(79, '#'))

    parser = OptionParser()
    parser.add_option("-c", "--channel", dest="channel_name",
                      help="runs the channel named CHANNEL_NAME",
                      metavar="CHANNEL_NAME")
    parser.add_option("-v", action="count", dest="verbosity",
                      help=("Application verbosity. Can be repeated up to 5 "
                            "times, each time increasing verbosity). If not "
                            "set, the logging configuration file will take "
                            "precedence."))

    options, _ = parser.parse_args()

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
        LOG.setLevel(verbosity_map[options.verbosity])
    elif options.verbosity and options.verbosity > len(verbosity_map):
        LOG.setLevel(logging.DEBUG)

    app = Application()
    signal.signal(signal.SIGINT, app.handle_sigint)
    app.run_channel(options.channel_name)
