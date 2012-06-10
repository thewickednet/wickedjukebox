import sys
import logging
import logging.config

__version__ = '2.1b1'


def setup_logging():
    try:
        logging.config.fileConfig("logging.ini")
    except IOError:
        print >>sys.stderr, ("Unable to open logging files. Make sure there "
                             "exists a folder 'logs' in the project root and "
                             "is writable!")
