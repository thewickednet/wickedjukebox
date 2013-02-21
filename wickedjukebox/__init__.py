import os
import logging
import logging.config


__version__ = '2.1b2'


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
    from pkg_resources import resource_filename

    logging.config.fileConfig(
        resource_filename('wickedjukebox', 'resources/logging.ini'))

    logging_conf_name = "logging.ini"
    log = logging.getLogger(__name__)
    log.info('Default logging loaded. You can override any log levels by '
            'creating a file called "{0}" in the folder specified in '
            'the {1} environment variable.'.format(
                logging_conf_name, ENV_CONF))

    if ENV_CONF in os.environ:
        logging_conf_name = os.path.join(os.environ[ENV_CONF],
                                         logging_conf_name)

    try:
        logging.config.fileConfig(logging_conf_name)
    except Exception, exc:
        log.error(exc)
    except IOError:
        print log.error(str(exc))
