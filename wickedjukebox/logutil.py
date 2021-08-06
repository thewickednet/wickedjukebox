
from typing import Any


def qualname(instance: Any) -> str:
    """
    Returns a qualified name for an object instance class.
    """
    cls = instance.__class__
    module = cls.__module__
    if module == '__builtin__':
        return cls.__name__
    return ".".join([module, cls.__name__])