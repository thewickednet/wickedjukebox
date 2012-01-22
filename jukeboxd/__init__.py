"""
The core module functionality for the jukebox daemon.

When importing this module, it will automatically search and load a config
from a given search path. The default search path is:

1. ~/.jukeboxd/config.ini
2. /etc/jukeboxd/config.ini

The search process can be controlled using environment variables:

* The path can be overridden using the JUKEBOX_PATH environment variable.
* The filename can be overridden using the JUKEBOX_CONFIG environment
  variable.

An example config file can be found in the project source tree under the name
"config.ini.dist"
"""

from ConfigParser import SafeConfigParser
from os import getenv, pathsep
from os.path import expanduser, join, exists
import logging
import sys

LOG = logging.getLogger(__name__)

def find_config():
    """
    Searches for an appropriate config file. If none is found, return None
    """

    path = [expanduser('~/.jukeboxd'), '/etc/jukeboxd']
    env_path = getenv("JUKEBOX_PATH")
    config_filename = getenv("JUKEBOX_CONFIG", "config.ini")
    if env_path:
        path = env_path.split(pathsep)

    detected_conf = None
    for dir in path:
        conf_name = join(dir, config_filename)
        if exists(conf_name):
            detected_conf = conf_name
            break
    return detected_conf, path

def load_config():
    """
    Actually load the config file.
    Raises an OSError if no file was found.
    """

    conf, path = find_config()
    if not conf:
        raise OSError("No config file found! Search path was %r" % path)

    parser = SafeConfigParser()
    parser.read(conf)
    LOG.info("Loaded settings from %r" % conf)
    return parser

try:
    CONF = load_config()
except OSError, ex:
    # Preventing a stack-trace. It looks too scary to a lot of people ;)
    LOG.critical(str(ex))
    sys.exit(1)
