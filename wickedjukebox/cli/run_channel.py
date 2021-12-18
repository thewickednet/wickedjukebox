"""
Entry points, and helpers for the command line interface.
"""
import logging
import sys
from argparse import ArgumentParser, Namespace
from typing import Optional

from wickedjukebox import __version__
from wickedjukebox.channel import Channel
from wickedjukebox.components import get_autoplay, get_ipc, get_player
from wickedjukebox.jingle import FileBasedJingles
from wickedjukebox.logutil import setup_logging

LOG = logging.getLogger(__name__)


class UnknownPlayer(Exception):
    """
    Raised if we have an unknown player instance.
    """


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
        default=0,
        help=(
            "Application verbosity. Can be repeated up to 5 "
            "times, each time increasing verbosity). If not "
            "set, the logging configuration file will take "
            "precedence."
        ),
    )
    args = parser.parse_args()
    return args


def make_channel(channel_name: str) -> Optional[Channel]:

    player = get_player(channel_name)
    autoplay = get_autoplay(channel_name)
    ipc = get_ipc(channel_name)
    channel = Channel(
        channel_name,
        random=autoplay,
        jingle=FileBasedJingles("mp3s/Jingles"),  # TODO
        player=player,
        ipc=ipc,
        tick_interval_s=10,
    )
    return channel


def main():
    """
    Parse command line options, bootstrap the app and run the channel
    """
    args = parse_args()
    setup_logging(args.verbosity)
    LOG.info("Wicked Jukebox v%s ", __version__)
    channel = make_channel(args.channel_name)
    if not channel:
        print(
            f"Unable to initialised channel {args.channel_name!r}",
            file=sys.stderr,
        )
        return -1

    channel.run()
