"""
Entry points, and helpers for the command line interface.
"""
import logging
import sys
from argparse import ArgumentParser, Namespace
from typing import Optional

from wickedjukebox import __version__
from wickedjukebox.channel import Channel
from wickedjukebox.component import (
    get_autoplay,
    get_ipc,
    get_jingle,
    get_player,
    get_queue,
)
from wickedjukebox.config import Config, ConfigKeys
from wickedjukebox.logutil import setup_logging
from wickedjukebox.model.db.sameta import connect

LOG = logging.getLogger(__name__)


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

    config = Config()
    player = get_player(config, channel_name)
    autoplay = get_autoplay(config, channel_name)
    ipc = get_ipc(config, channel_name)
    queue = get_queue(config, channel_name)
    jingle = get_jingle(config, channel_name)
    channel = Channel(
        channel_name,
        random=autoplay,
        jingle=jingle,
        player=player,
        ipc=ipc,
        queue=queue,
        tick_interval_s=10,
    )
    return channel


def main():
    """
    Parse command line options, bootstrap the app and run the channel
    """
    args = parse_args()
    setup_logging(args.verbosity)
    config = Config()
    dsn = config.get(ConfigKeys.DSN)
    connect(dsn)
    LOG.info("Wicked Jukebox v%s ", __version__)
    channel = make_channel(args.channel_name)
    if not channel:
        print(
            f"Unable to initialised channel {args.channel_name!r}",
            file=sys.stderr,
        )
        return -1

    channel.run()
