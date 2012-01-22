from os.path import isfile, isdir, join
from os import walk
import logging
import sys

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

LOG = logging.getLogger(__name__)

def scan_file(path):
    audio = MP3(path, ID3=EasyID3)
    print 80*"-"
    print audio.pprint()

def scan(path):
    if isfile(path):
        scan_file(path)
    elif isdir(path):
        for root, dirs, files in walk(path):
            for name in files:
                scan_file(join(root, name))

def cli_scan():
    from optparse import OptionParser
    usage = "%prog [options] <dirname|filename>"
    parser = OptionParser(usage)
    options, args = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        sys.exit(1)

    scan(args[0])

