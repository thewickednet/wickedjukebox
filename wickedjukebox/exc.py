"""
This module contains exceptions for the wickedjukebox package
"""


class WickedJukeboxException(Exception):
    """
    The parent exception for errors originating from the wickedjukebox code-base
    """


class ConfigError(WickedJukeboxException):
    """
    An error which is raised if something is broken in the application config
    and we cannot continue
    """
