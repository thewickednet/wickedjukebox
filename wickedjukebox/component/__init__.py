"""
This package contains the implementation for the modular components in
wickedjukebox.

Modular components define behaviour that can be changed via the config file.
"""
import logging

from wickedjukebox.component.ipc import DBIPC, FSIPC, AbstractIPC, NullIPC
from wickedjukebox.component.player import AbstractPlayer, MpdPlayer, NullPlayer
from wickedjukebox.component.queue import (
    AbstractQueue,
    DatabaseQueue,
    NullQueue,
)
from wickedjukebox.component.random import (
    AbstractRandom,
    AllFilesRandom,
    NullRandom,
    SmartPrefetch,
)
from wickedjukebox.config import Config, ConfigKeys
from wickedjukebox.exc import ConfigError

LOG = logging.getLogger(__name__)


def get_player(channel_name: str) -> AbstractPlayer:
    """
    Construct the configured player-backend using the channel-name
    """
    player_type = Config.get(
        ConfigKeys.PLAYER, channel=channel_name, fallback=""
    )
    if player_type.strip() == "":
        LOG.warning("Config-value 'player' is missing. Using NULL-player!")
        player_type = "null"

    player = None
    clsmap = {
        "mpd": MpdPlayer,
        "null": NullPlayer,
    }
    cls = clsmap.get(player_type, None)
    if cls:
        player = cls()
        player_settings = Config.dictify(
            ConfigKeys.PLAYER, channel_name, cls.CONFIG_KEYS
        )
        player.configure(player_settings)
        return player

    raise ConfigError(
        f"Unknown player {player_type!r} defined in config for "
        f"channel {channel_name!r}"
    )


def get_autoplay(channel_name: str) -> AbstractRandom:
    autoplay_type = Config.get(
        ConfigKeys.AUTOPLAY, channel=channel_name, fallback=""
    )
    # TODO: This function is very similar to get_player and can likely be merged
    if autoplay_type.strip() == "":
        LOG.warning(
            "Config-value %r is missing. Disabling auto-play",
            str(ConfigKeys.AUTOPLAY),
        )
        autoplay_type = "null"

    instance = None
    clsmap = {
        "allfiles_random": AllFilesRandom,
        "smart_prefetch": SmartPrefetch,
        "null": NullRandom,
    }
    cls = clsmap.get(autoplay_type, None)
    if cls:
        instance = cls(channel_name)
        autoplay_settings = Config.dictify(
            ConfigKeys.AUTOPLAY, channel_name, cls.CONFIG_KEYS
        )
        instance.configure(autoplay_settings)
        return instance

    raise ConfigError(
        f"Unknown autoplay-mode {autoplay_type!r} defined in config for "
        f"channel {channel_name!r}"
    )


def get_ipc(channel_name: str) -> AbstractIPC:
    ipc_type = Config.get(ConfigKeys.IPC, channel=channel_name, fallback="")
    # TODO: This function is very similar to get_player and can likely be merged
    if ipc_type.strip() == "":
        LOG.warning(
            "Config-value %r is missing. Disabling auto-play",
            str(ConfigKeys.IPC),
        )
        ipc_type = "null"

    instance = None
    clsmap = {
        "null": NullIPC,
        "fs": FSIPC,
        "db": DBIPC,
    }
    cls = clsmap.get(ipc_type, None)
    if cls:
        instance = cls(channel_name)
        ipc_settings = Config.dictify(
            ConfigKeys.IPC, channel_name, cls.CONFIG_KEYS
        )
        instance.configure(ipc_settings)
        return instance

    raise ConfigError(
        f"Unknown player {ipc_type!r} defined in config for "
        f"channel {channel_name!r}"
    )


def get_queue(channel_name: str) -> AbstractQueue:
    queue_type = Config.get(
        ConfigKeys.QUEUE_MODEL, channel=channel_name, fallback=""
    )
    # TODO: This function is very similar to get_player and can likely be merged
    if queue_type.strip() == "":
        LOG.warning(
            "Config-value %r is missing. Disabling queue",
            str(ConfigKeys.QUEUE_MODEL),
        )
        queue_type = "null"

    instance = None
    clsmap = {
        "null": NullQueue,
        "db": DatabaseQueue,
    }
    cls = clsmap.get(queue_type, None)
    if cls:
        instance = cls(channel_name)
        queue_settings = Config.dictify(
            ConfigKeys.QUEUE_MODEL, channel_name, cls.CONFIG_KEYS
        )
        instance.configure(queue_settings)
        return instance

    raise ConfigError(
        f"Unknown queue {queue_type!r} defined in config for "
        f"channel {channel_name!r}"
    )
