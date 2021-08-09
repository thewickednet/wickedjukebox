"""
Entry points, and helpers for the command line interface.
"""
import logging
from argparse import ArgumentParser, Namespace
from os import getenv
from pathlib import Path

from wickedjukebox import __version__, setup_logging
from wickedjukebox.channel import Channel
from wickedjukebox.jingle import FileBasedJingles
from wickedjukebox.player import MpdPlayer, PathMap
from wickedjukebox.random import AllFilesRandom

LOG = logging.getLogger(__name__)


def set_log_verbosity(verbosity: int) -> None:
    verbosity_map = {
        5: logging.DEBUG,
        4: logging.INFO,
        3: logging.WARN,
        2: logging.ERROR,
        1: logging.CRITICAL,
    }
    verbosity = verbosity_map.get(verbosity, logging.DEBUG)
    logging.getLogger().setLevel(verbosity)


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "-c",
        "--channel",
        dest="channel_name",
        help="runs the channel named CHANNEL_NAME",
        metavar="CHANNEL_NAME",
    )
    parser.add_argument(
        "-v",
        action="count",
        dest="verbosity",
        help=(
            "Application verbosity. Can be repeated up to 5 "
            "times, each time increasing verbosity). If not "
            "set, the logging configuration file will take "
            "precedence."
        ),
    )
    args = parser.parse_args()
    return args


def make_channel(channel_name: str) -> Channel:
    # TODO: Read these value from the channel-config in the database
    mpd_host = getenv("MPD_HOST", "127.0.0.1")
    mpd_port = int(getenv("MPD_PORT", 6600))
    channel = Channel(
        channel_name,
        random=AllFilesRandom("mp3s/Tagged"),
        jingle=FileBasedJingles("mp3s/Jingles"),
        player=MpdPlayer(
            host=mpd_host,
            port=mpd_port,
            path_map=PathMap(
                Path("/home/exhuma/work/wickedjukebox/mp3s"),
                Path("/var/lib/mp3s/music"),
            ),
        ),
        tick_interval_s=10,
    )
    return channel


def main():
    """
    Parse command line options, bootstrap the app and run the channel
    """
    setup_logging()
    LOG.info(" Wicked Jukebox %s", __version__.center(79, "#"))
    args = parse_args()
    set_log_verbosity(args.verbosity)
    channel = make_channel(args.channel_name)
    channel.run()
