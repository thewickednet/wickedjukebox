# pylint: disable=missing-docstring
"""
Utility methods
"""

import logging
import sys

LOG = logging.getLogger(__name__)

ENCODINGS = [
    'latin-1',
    'utf-8',
    sys.getfilesystemencoding(),
]

FS_CODING = sys.getfilesystemencoding()

# prepare encodings in reversed order for fs-encoding
REVENCODINGS = ENCODINGS
REVENCODINGS.reverse()


def fsencode(filename):
    if not isinstance(filename, unicode):
        # no need to re-encode
        return filename

    try:
        return filename.encode(FS_CODING)
    except UnicodeEncodeError:
        LOG.error("Filename %r is not encoded using the registered "
                  "filesystem encoding!", filename)
        return None


def fsdecode(filename):
    LOG.debug("Trying to decode %r using %r.", filename, FS_CODING)
    if isinstance(filename, unicode):
        # no need to redecode
        return filename

    try:
        decoded = (filename.decode(FS_CODING), FS_CODING)
        LOG.debug("Encoded as %r", decoded)
    except UnicodeDecodeError:
        LOG.error("Filename %r is not encoded using the registered filesystem "
                  "encoding!", filename)
        return (None, None)
    return decoded


def direxists(name):
    import os.path
    if not os.path.exists(name):
        LOG.warning("'%s' does not exist!", name)
        return False
    return True
