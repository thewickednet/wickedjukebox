"""
Utility methods
"""

import os
import ConfigParser
import logging
LOG = logging.getLogger(__name__)

def load_config(filename, config={}):
    """
    returns a dictionary with key's of the form
    <section>.<option> and the values.

    from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65334
    """
    if not os.path.exists( filename ):
        raise ValueError, 'Cannot find configfile "%s"' % filename
    config = config.copy()
    parser = ConfigParser.ConfigParser()
    parser.read(filename)
    for sec in parser.sections():
        name = sec.lower()
        for opt in parser.options(sec):
            config[name + "." + opt.lower()] = unicode(
                    parser.get(sec, opt)).strip()
    return config

def direxists(dirname):
    """
    Wrapper around ``os.path.exists`` with the addition that missing folders
    are logged.

    :param dirname: The folder to test.
    """
    if not os.path.exists(dirname):
        LOG.warning( "'%s' does not exist!" % dirname )
        return False
    else:
        return True
