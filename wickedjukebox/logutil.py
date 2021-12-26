"""
This module contains some helpers that come in handy during logging
"""

import logging
import logging.config
import traceback
from typing import Any, Type, TypeVar

import gouge.colourcli as gc

_T = TypeVar("_T", bound=Type[Any])


def caller_source():
    """
    Returns the source line from the stack-frame *before* the call of
    *caller_source*.

    For example, if the stack is something like this::

        main()
            myfunction()
                my_inner_function()
                    source = caller_source()

    Then *source* will point to ``myfunction``!
    """
    stack = traceback.extract_stack()
    source = stack[-2]
    return source


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
