"""
Entry points, and helpers for the command line interface.
"""
import logging
import sys
from argparse import ArgumentParser, Namespace
from typing import Optional

from wickedjukebox import __version__
from wickedjukebox.channel import Channel
from wickedjukebox.config import (
    Config,
    ConfigKeys,
    get_config_files,
    parse_param_string,
)
from wickedjukebox.exc import ConfigError
from wickedjukebox.jingle import FileBasedJingles
from wickedjukebox.logutil import setup_logging
from wickedjukebox.player import AbstractPlayer, MpdPlayer, NullPlayer
from wickedjukebox.random import AllFilesRandom

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


def get_player(channel_name: str) -> AbstractPlayer:
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
            raise ConfigError(
                f"Missing config-key {key!r} in 'player_settings' "
                f"{player_settings_str!r} for channel {channel_name!r} "
                f"(set in one of {get_config_files()})",
            ) from exc
        return player

    raise ConfigError(
        f"Unknown player {player_type!r} defined in config for "
        "channel {channel_name!r}"
    )


def make_channel(channel_name: str) -> Optional[Channel]:

    player = get_player(channel_name)
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
    args = parse_args()
    setup_logging(args.verbosity)
    LOG.info(" Wicked Jukebox %s", __version__.center(79, "#"))
    channel = make_channel(args.channel_name)
    if not channel:
        print(
            f"Unable to initialised channel {args.channel_name!r}",
            file=sys.stderr,
        )
        return -1

    channel.run()
