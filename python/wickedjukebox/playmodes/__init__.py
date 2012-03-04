"""
This module contains different playmodes. This encompasses both random and
queue strategies.
"""

def create(modname):
    """
    A factory method, which returns the imported module
    """
    if modname in globals():
        return reload(globals()[modname])

    module = 'demon.playmodes.%s' % modname
    __import__(module)
    return globals()[modname]
