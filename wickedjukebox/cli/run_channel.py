"""
Entry points, and helpers for the command line interface.
"""
import logging
import sys
from argparse import ArgumentParser, Namespace
from typing import Optional

from wickedjukebox import __version__, setup_logging
from wickedjukebox.channel import Channel
from wickedjukebox.config import (
    Config,
    ConfigKeys,
    get_config_files,
    parse_param_string,
)
from wickedjukebox.jingle import FileBasedJingles
from wickedjukebox.player import MpdPlayer, NullPlayer
from wickedjukebox.random import AllFilesRandom

LOG = logging.getLogger(__name__)


class UnknownPlayer(Exception):
    """
    Raised if we have an unknown player instance.
    """


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


def make_channel(channel_name: str) -> Optional[Channel]:
    player_type = Config.get(
        ConfigKeys.PLAYER, channel=channel_name, fallback=""
    )
    if player_type == "":
        LOG.warning("Config-value 'player' is missing. Using NULL-player!")
        player_type = "null"

    player_settings_str = Config.get(
        ConfigKeys.PLAYER_SETTINGS, channel=channel_name, fallback=""
    )

    player_settings = parse_param_string(player_settings_str)
    player = None
    clsmap = {
        "mpd": MpdPlayer,
        "null": NullPlayer,
    }
    cls = clsmap.get(player_type, None)
    if cls:
        player = cls()
        try:
            player.configure(player_settings)
        except KeyError as exc:
            key = exc.args[0]
            print(
                f"Missing config-key {key!r} in 'player_settings' "
                f"{player_settings_str!r} for channel {channel_name!r}"
                f"(set in one of {get_config_files()})",
                file=sys.stderr,
            )
            return None
    else:
        raise UnknownPlayer(player_type)

    channel = Channel(
        channel_name,
        random=AllFilesRandom("mp3s/Tagged"),
        jingle=FileBasedJingles("mp3s/Jingles"),
        player=player,
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
    if not channel:
        print(
            f"Unable to initialised channel {args.channel_name!r}",
            file=sys.stderr,
        )
        return -1

    channel.run()
