# pylint: disable=missing-docstring

import importlib.metadata
import logging
import logging.config
import os


__version__ = importlib.metadata.version("wickedjukebox")


ENV_CONF = 'WICKEDJB_CONFIG_FOLDER'
"The name of the environment variable controlling the config location"


def setup_logging():
    from pkg_resources import resource_filename
    from os.path import exists

    logging.config.fileConfig(
        resource_filename('wickedjukebox', 'resources/logging.ini'))

    logging_conf_name = "logging.ini"
    log = logging.getLogger(__name__)
    logging.getLogger('requests').setLevel(logging.WARNING)
    log.info('Default logging loaded. You can override any log levels by '
             'creating a file called "%s" in the folder specified in '
             'the %s environment variable.', logging_conf_name, ENV_CONF)

    if ENV_CONF in os.environ:
        logging_conf_name = os.path.join(os.environ[ENV_CONF],
                                         logging_conf_name)

    if exists(logging_conf_name):
        try:
            logging.config.fileConfig(logging_conf_name,
                                      disable_existing_loggers=False)
            log.info('Additional log config read from %s', logging_conf_name)
        except IOError:
            print(log.error(str(exc)))
        except Exception:  # pylint: disable=broad-except
            log.error("Error reading from %r!",
                      logging_conf_name, exc_info=True)
