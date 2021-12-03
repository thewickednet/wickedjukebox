"""
This module contains helpers for application configuration
"""

import logging
from configparser import ConfigParser
from enum import Enum
from typing import Any, Callable, Dict, List, NamedTuple, Type, TypeVar

from config_resolver import get_config

T = TypeVar("T", bound=Type[Any])
NO_DEFAULT = object()
LOG = logging.getLogger(__name__)


class ConfigScope(Enum):
    CORE = "core"
    CHANNEL = "channel"


class ConfigOption(NamedTuple):
    scope: ConfigScope
    section: str
    subsection: str


def parse_param_string(value: str) -> Dict[str, str]:
    """
    Parse a "key=value" list into a dictionary.

    >>> parse_param_string("a=2, b=20, c=hello")
    {'a': '2', 'b': '20', 'c': 'hello'}
    """
    output: Dict[str, str] = {}
    if value:
        for param in value.split(","):
            key, _, value = param.partition("=")
            output[key.strip()] = value.strip()
    return output


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


def get_config_files() -> List[str]:
    """
    Return a list of config-files which are used by this application
    """
    _, meta = default_config()
    return meta.active_path


def load_config() -> ConfigParser:
    """
    Loads the application config.
    """
    cfg, _ = default_config()
    return cfg


class ConfigKeys(Enum):
    """
    A well-defined list of config-values in the config-file with the sections
    they are expected to be in.
    """

    CHANNEL_CYCLE = ConfigOption(ConfigScope.CHANNEL, "channel_cycle", "")
    JINGLES_FOLDER = ConfigOption(ConfigScope.CHANNEL, "jingles_folder", "")
    JINGLES_INTERVAL = ConfigOption(ConfigScope.CHANNEL, "jingles_interval", "")
    LASTFM_API_KEY = ConfigOption(ConfigScope.CORE, "lastfm_api_key", "")
    MAX_CREDITS = ConfigOption(ConfigScope.CORE, "max_credits", "")
    MAX_RANDOM_DURATION = ConfigOption(
        ConfigScope.CORE, "max_random_duration", ""
    )
    PROOFOFLIFE_TIMEOUT = ConfigOption(
        ConfigScope.CORE, "proofoflife_timeout", ""
    )
    QUEUE_MODEL = ConfigOption(ConfigScope.CORE, "queue_model", "")
    RANDOM_MODEL = ConfigOption(ConfigScope.CORE, "random_model", "")
    SCORING_LASTPLAYED = ConfigOption(
        ConfigScope.CORE, "scoring_lastplayed", ""
    )
    SCORING_NEVERPLAYED = ConfigOption(
        ConfigScope.CORE, "scoring_neverplayed", ""
    )
    SCORING_RANDOMNESS = ConfigOption(
        ConfigScope.CORE, "scoring_randomness", ""
    )
    SCORING_SONGAGE = ConfigOption(ConfigScope.CORE, "scoring_songage", "")
    SCORING_USERRATING = ConfigOption(
        ConfigScope.CORE, "scoring_userrating", ""
    )
    SYS_UTCTIME = ConfigOption(ConfigScope.CORE, "sys_utctime", "")
    RECENCY_THRESHOLD = ConfigOption(ConfigScope.CORE, "recency_threshold", "")
    PLAYER_SETTINGS = ConfigOption(ConfigScope.CHANNEL, "player", "settings")
    PLAYER = ConfigOption(ConfigScope.CHANNEL, "player", "backend")

    AUTOPLAY = ConfigOption(ConfigScope.CHANNEL, "autoplay", "type")
    AUTOPLAY_SETTINGS = ConfigOption(
        ConfigScope.CHANNEL, "autoplay", "settings"
    )

    IPC = ConfigOption(ConfigScope.CHANNEL, "ipc", "type")
    IPC_SETTINGS = ConfigOption(ConfigScope.CHANNEL, "ipc", "settings")


class Config:
    @staticmethod
    def get(
        key: ConfigKeys,
        fallback: T = NO_DEFAULT,
        channel: str = "",
        converter: Callable[[str], T] = lambda x: x,
    ) -> T:
        config = load_config()
        scope, section, option = key.value
        if scope == ConfigScope.CHANNEL:
            section = f"channel:{channel}:{section}"
        else:
            section = "core"
        if fallback is NO_DEFAULT:
            value = config.get(section, option)
        else:
            value = config.get(section, option, fallback=fallback)
        return converter(value)
