"""
This package contains the implementation for the modular components in
wickedjukebox.

Modular components define behaviour that can be changed via the config file.
"""
import logging
from typing import Any, Callable, Mapping, Type, TypeVar

from wickedjukebox.component.ipc import DBIPC, FSIPC, AbstractIPC, NullIPC
from wickedjukebox.component.jingle import (
    AbstractJingle,
    FileBasedJingles,
    NullJingle,
)
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
_T = TypeVar(
    "_T", bound=Any
)  # TODO: Investigate how we could mark this up with covariance in mind


def make_component_getter(
    config_key: ConfigKeys,
    clsmap: Mapping[str, Type[_T]],
    return_type: Type[_T],
) -> Callable[[Config, str], _T]:
    """
    Create a function that can be used to instantiate and configure a component
    for the jukebox.

    :param config_key: The config section/option which contains the component
        settings.
    :param clsmap: A mapping from a "type" to a class for that type. The key
        ("type") is a value from the config-file and the value must be a class
        implementing a component of that type.
    :param return_type: An indicator for the type-checker defining the
        "interface" of the returned component.
    """

    def get_component(config: Config, channel_name: str) -> return_type:
        component_type = config.get(
            config_key, channel=channel_name, fallback=""
        )
        if component_type.strip() == "":
            LOG.warning(
                "Config-value %r is missing. Using 'null' as fallback",
                str(config_key),
            )
            component_type = "null"

        instance = None
        cls = clsmap.get(component_type, None)
        if cls:
            instance = cls(config, channel_name)
            component_settings = config.dictify(
                config_key, channel_name, cls.CONFIG_KEYS
            )
            instance.configure(component_settings)
            return instance

        raise ConfigError(
            f"Unknown component-type {component_type!r} defined in config for "
            f"channel {channel_name!r}"
        )

    return get_component


get_player = make_component_getter(
    ConfigKeys.PLAYER,
    {
        "mpd": MpdPlayer,
        "null": NullPlayer,
    },
    AbstractPlayer,
)

get_autoplay = make_component_getter(
    ConfigKeys.AUTOPLAY,
    {
        "allfiles_random": AllFilesRandom,
        "smart_prefetch": SmartPrefetch,
        "null": NullRandom,
    },
    AbstractRandom,
)

get_ipc = make_component_getter(
    ConfigKeys.IPC,
    {
        "null": NullIPC,
        "fs": FSIPC,
        "db": DBIPC,
    },
    AbstractIPC,
)

get_queue = make_component_getter(
    ConfigKeys.QUEUE_MODEL,
    {
        "null": NullQueue,
        "db": DatabaseQueue,
    },
    AbstractQueue,
)


get_jingle = make_component_getter(
    ConfigKeys.JINGLE_MODEL,
    {
        "null": NullJingle,
        "fs": FileBasedJingles,
    },
    AbstractJingle,
)
