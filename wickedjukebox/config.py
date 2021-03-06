"""
This module contains helpers for application configuration
"""

import logging
from configparser import ConfigParser
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    NamedTuple,
    Optional,
    Set,
    TypeVar,
    Union,
)

from config_resolver.core import get_config

from wickedjukebox.exc import ConfigError

TFallback = TypeVar("TFallback", bound=Any)
LOG = logging.getLogger(__name__)


class Sentinel:
    """
    Helper class to type-check "unset" variables.
    """


NO_DEFAULT = Sentinel()


class ConfigScope(Enum):
    """
    Possible "scopes" for config values. Each scope has slightly different
    semantics on how to find the appropriate section/option.
    """

    CORE = "core"
    "Core values are in the [core] section"
    CHANNEL = "channel"
    "Channel values are in the [channel:<channel-name>...] section"


class ConfigOption(NamedTuple):
    """
    A helper class to define where a configuration value can be found

    This allows defining section headers with more meta-information like
    "channel-kontext" and "subsection". For example a value scoped to a channel
    with the name "test-channel" in subsection "player" is located in the
    ini-section: ``[channel:test-channel:player]``
    """

    scope: ConfigScope
    "How 'global' a value is"
    section: str
    "The section in which to find the option"
    subsection: str
    "The subsection is defined as part of the section-name"


def default_config():
    """
    Return a default config lookup-result
    """
    return get_config(
        "wickedjukebox",
        group_name="wicked",
        lookup_options={
            "filename": "config.ini",
            "require_load": True,
        },
    )


class ConfigKeys(Enum):
    """
    A well-defined list of config-values in the config-file with the sections
    they are expected to be in.
    """

    DSN = ConfigOption(ConfigScope.CORE, "", "dsn")
    PLAYER = ConfigOption(ConfigScope.CHANNEL, "player", "type")
    AUTOPLAY = ConfigOption(ConfigScope.CHANNEL, "autoplay", "type")
    IPC = ConfigOption(ConfigScope.CHANNEL, "ipc", "type")
    QUEUE = ConfigOption(ConfigScope.CHANNEL, "queue", "type")
    JINGLE = ConfigOption(ConfigScope.CHANNEL, "jingle", "type")

    def __str__(self) -> str:
        return (
            f"[{self.value.scope.value}:<channel-name>:{self.value.section}] / "
            f"{self.value.subsection}"
        )


class Config:
    """
    The Config class provides an abstraction around config-file values
    """

    def __init__(self, config: Optional[ConfigParser] = None) -> None:
        self.config = config

    @staticmethod
    def get_section(key: ConfigOption, channel: str):
        """
        Get the section linked to a given config-option for a given channel.
        """
        scope, section, _ = key
        if scope == ConfigScope.CHANNEL:
            section = f"channel:{channel}:{section}"
        else:
            section = "core"
        return section

    def load_config(self) -> ConfigParser:
        """
        Loads the application config.
        """
        if self.config is None:
            self.config, _ = default_config()
        return self.config

    def get(
        self,
        key: ConfigKeys,
        fallback: Union[TFallback, Sentinel] = NO_DEFAULT,
        channel: str = "",
        converter: Callable[[str], TFallback] = lambda x: x,
    ) -> TFallback:
        """
        Retrieve a config-value for a given config-key
        """
        config = self.load_config()
        section = Config.get_section(key.value, channel)
        _, _, option = key.value
        if fallback is NO_DEFAULT:
            value = config.get(section, option)
        else:
            value = str(config.get(section, option, fallback=fallback))
        return converter(value)

    def dictify(self, key: ConfigKeys, channel: str, keys: Set[str]):
        """
        Convert a given section to a simple Python dictionary.

        :param key: The config key to convert
        :param channel: The channel-name
        :param keys: Expect exactly these keys in the options. If a difference
            is detectd, raise a ConfigError
        """
        config = self.load_config()
        section = Config.get_section(key.value, channel)
        output: Dict[str, str] = {}
        missing_keys: Set[str] = set()
        for option in config.options(section):
            if option in keys:
                if config.has_option(section, option):
                    output[option] = config.get(section, option)
        missing_keys = keys - set(output.keys())
        if missing_keys:
            raise ConfigError(
                f"The config-section {section!r} is missing "
                f"the keys {sorted(missing_keys)!r}"
            )
        return output
