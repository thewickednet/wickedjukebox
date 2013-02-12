import os
import sys
import logging
import logging.config

import pkg_resources


__version__ = pkg_resources.resource_string(__name__, 'version.txt').strip()


ENV_CONF = 'WICKEDJB_CONFIG_FOLDER'
"The name of the environment variable controlling the config location"


def load_config():
    """
    Loads the application config.
    """
    from config_resolver import Config
    clog = logging.getLogger('config_resolver')
    stderr = logging.StreamHandler()
    stderr.setLevel(logging.WARNING)
    clog.addHandler(stderr)
    cfg = Config('wicked', 'wickedjukebox', filename='config.ini')
    if not cfg.loaded_files:
        raise IOError('No valid config file found. Search path was: %s' % (
            cfg.active_path))
    return cfg


def setup_logging():
    logging_conf_name = "logging.ini"
    if ENV_CONF in os.environ:
        logging_conf_name = os.path.join(os.environ[ENV_CONF],
                                         logging_conf_name)

    try:
        logging.config.fileConfig(logging_conf_name)
    except Exception, exc:
        print >>sys.stderr, ("""\
------------------------------------------------------------------------------
WARNING: There was an error loading the logging configuration! The received
         error message was:

            %s.

         It may simply be the case, that the logging configuration file named:
             %s
         was not found. If you have it in a different folder, you can override
         the default folder using the environment vairable:
            %s.

         If the file exists, and you get other errors, consult the
         documentation for the python 'logging' package.
------------------------------------------------------------------------------
""" % (
        exc, logging_conf_name, ENV_CONF,))

    except IOError:
        print >>sys.stderr, ("""\
WARNING: Unable to open logging files. Make sure there exists a folder 'logs'
         in the project root and is writable!""")
