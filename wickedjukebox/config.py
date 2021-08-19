"""
This module contains helpers for application configuration
"""

from configparser import ConfigParser
from enum import Enum
from typing import Any, Callable, Dict, List, Type, TypeVar

from config_resolver import get_config

T = TypeVar("T", bound=Type[Any])
NO_DEFAULT = object()


def parse_param_string(value: str) -> Dict[str, str]:
    """
    Parse a "key=value" list into a dictionary.

    >>> parse_param_string("a=2, b=20, c=hello")
    {'a': '2', 'b': '20', 'c': 'hello'}
    """
    output = {}
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
    CHANNEL_CYCLE = ("channel", "channel_cycle")
    JINGLES_FOLDER = ("channel", "jingles_folder")
    JINGLES_INTERVAL = ("channel", "jingles_interval")
    LASTFM_API_KEY = ("core", "lastfm_api_key")
    MAX_CREDITS = ("core", "max_credits")
    MAX_RANDOM_DURATION = ("core", "max_random_duration")
    PROOFOFLIFE_TIMEOUT = ("core", "proofoflife_timeout")
    QUEUE_MODEL = ("core", "queue_model")
    RANDOM_MODEL = ("core", "random_model")
    SCORING_LASTPLAYED = ("core", "scoring_lastplayed")
    SCORING_NEVERPLAYED = ("core", "scoring_neverplayed")
    SCORING_RANDOMNESS = ("core", "scoring_randomness")
    SCORING_SONGAGE = ("core", "scoring_songage")
    SCORING_USERRATING = ("core", "scoring_userrating")
    SYS_UTCTIME = ("core", "sys_utctime")
    RECENCY_THRESHOLD = ("core", "recency_threshold")
    PLAYER_SETTINGS = ("core", "player_settings")
    PLAYER = ("core", "player")


class Config:
    @staticmethod
    def get(
        key: ConfigKeys,
        fallback: T = NO_DEFAULT,
        channel: str = "",
        converter: Callable[[str], T] = lambda x: x,
    ) -> T:
        config = load_config()
        section, option = key.value
        if channel:
            section = f"channel:{channel}"
        if fallback is NO_DEFAULT:
            value = config.get(section, option)
        else:
            value = config.get(section, option, fallback=fallback)
        return converter(value)
