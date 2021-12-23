"""
This module contains some helpers that come in handy during logging
"""

import logging
import logging.config
from typing import Any, Type, TypeVar

import gouge.colourcli as gc

_T = TypeVar("_T", bound=Type[Any])


def qualname(instance: Any) -> str:
    """
    Returns a qualified name for an object instance class.
    """
    cls = instance.__class__
    module = cls.__module__
    if module == "__builtin__":
        return cls.__name__
    return ".".join([module, cls.__name__])


def setup_logging(verbosity: int = 0) -> None:
    """
    Configure logging for the application for a given verbosity level
    """
    levelmap = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }
    verbosity = max(0, min(verbosity, max(levelmap.keys())))
    gc.Simple.basicConfig(level=levelmap[verbosity])
    logging.getLogger("requests").setLevel(logging.WARNING)


def qualname_repr(cls: _T) -> _T:
    """
    Adds a simple __repr__ to a class returning the qualified name of the class
    """

    def __repr__(self: _T) -> str:
        return f"<{qualname(self)}>"

    cls.__repr__ = __repr__
    return cls
