"""
Utility methods
"""

import os
import ConfigParser
import logging
LOG = logging.getLogger(__name__)

def loadConfig(file, config={}):
    """
    returns a dictionary with key's of the form
    <section>.<option> and the values.

    from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65334
    """
    if not os.path.exists( file ):
        raise ValueError, 'Cannot find configfile "%s"' % file
    config = config.copy()
    cp = ConfigParser.ConfigParser()
    cp.read(file)
    for sec in cp.sections():
        name = sec.lower()
        for opt in cp.options(sec):
            config[name + "." + opt.lower()] = unicode(cp.get(sec, opt)).strip()
    return config

def direxists(dir):
    import os.path
    if not os.path.exists( dir ):
        LOG.warning( "'%s' does not exist!" % dir )
        return False
    else:
        return True
