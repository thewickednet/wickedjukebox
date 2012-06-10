import os
import sys
import logging
import logging.config
import ConfigParser

__version__ = '2.1b1'


ENV_CONF = 'WICKEDJB_CONFIG_FOLDER'
"The name of the environment variable controlling the config location"


def load_config(file, config={}):
    """
    returns a dictionary with key's of the form
    <section>.<option> and the values.

    from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65334
    """
    if ENV_CONF in os.environ:
        file = os.path.join(os.environ[ENV_CONF],
                            os.path.basename(file))

    if not os.path.exists(file):
        print >>sys.stderr, 'Cannot find configfile "%s"' % file
        print >>sys.stderr, ('You can set the %s environment variable to '
                             'specify the folder in which the file is '
                             'located!' % ENV_CONF)
        sys.exit(9)
    config = config.copy()
    cp = ConfigParser.ConfigParser()
    cp.read(file)
    for sec in cp.sections():
        name = sec.lower()
        for opt in cp.options(sec):
            config[name + "." + opt.lower()] = cp.get(sec, opt).strip()
    return config


def setup_logging():
    logging_conf_name = "logging.ini"
    if ENV_CONF in os.environ:
        logging_conf_name = os.path.join(os.environ[ENV_CONF],
                                         logging_conf_name)

    try:
        logging.config.fileConfig(logging_conf_name)
    except IOError:
        print >>sys.stderr, ("Unable to open logging files. Make sure there "
                             "exists a folder 'logs' in the project root and "
                             "is writable!")
