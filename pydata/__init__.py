import logging
import logging.config
def setup_logging():
    try:
        logging.config.fileConfig("logging.ini")
    except IOError, exc:
        print "Unable to open logging files. Make sure there exists a folder 'logs' in the project root and is writable!"
