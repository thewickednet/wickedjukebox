"""
This module contains helpers for application configuration
"""

from configparser import ConfigParser

from config_resolver import get_config


def load_config() -> ConfigParser:
    """
    Loads the application config.
    """
    cfg, _ = get_config(
        "wickedjukebox",
        group_name="wicked",
        lookup_options={
            "filename": "config.ini",
            "require_load": True,
        },
    )
    return cfg
