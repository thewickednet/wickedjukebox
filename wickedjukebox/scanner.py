"""
Audio file scanner module

This module contains everything needed to scan a directory of audio files an
store the metadata in the jukebox database
"""
from os import walk, path, sep, listdir
import sys
import logging

from sqlalchemy.sql import select

from wickedjukebox.util import fsdecode, fsencode
from wickedjukebox.demon.dbmodel import (
     Song,
     songTable,
     Session,
     Setting)

LOG = logging.getLogger(__name__)

EXTS = Setting.get("recognizedTypes", "").split(" ")


def is_valid_audio_file(path):
    return path.endswith(EXTS[0])


def process(localpath):

    if not localpath:
        LOG.warning( "Skipping undefined filename!" )
        return

    session = Session()

    if is_valid_audio_file(localpath):
        try:
            song = session.query(Song).filter_by( localpath=localpath ).first()
            if not song:
                song = Song(localpath, None, None)
            song.scan_from_file(localpath, sys.getfilesystemencoding())
            session.add(song)
            LOG.info( "%r" % (song) )
        except UnicodeDecodeError, ex:
            LOG.error( "Unable to decode %r (%s)" % (localpath, ex) )
    else:
        LOG.debug("%r is not a valid audio-file "
                  "(only scanning extensions %r)" % (localpath, EXTS))

    session.commit()
    session.close()


def do_housekeeping():
    """
    Database cleanup, and set other values that are difficult to read during
    scanning.
    """
    LOG.info( "Performing housekeeping. This may take a while!" )
    songs = select([songTable.c.localpath]).execute()
    for row in songs:
        try:
            if not path.exists( fsencode(row[0]) ):
                print `row[0]`, "removed from disk"
        except UnicodeEncodeError, e:
            LOG.error( "Unable to decode %r (%s)" % ( row[0], e) )

def processor_todatabase(root, localpath):
    session = Session()
    song = session.query(Song).filter_by( localpath=localpath ).first()
    if not song:
        song = Song(localpath, None, None)
    localpath, encoding = fsdecode( localpath )
    song.scan_from_file( localpath, encoding )
    session.add(song)
    LOG.debug( "%r at %r" % (song, localpath) )
    session.commit()
    session.close()

def scan(top, subfolder=u""):
    """
    Scans a folder rootet at <top> for audio files. It will scan the supfolder
    named in ``subfolder``. The "*" character can be used for globbing.

    @param top: The root folder to scan
    @param subfolder: The subfolder to scan.
    """
    from sys import stdout
    from wickedjukebox.util import TerminalController, ProgressBar

    tc = TerminalController()

    spinner_chars = r"/-\|"
    def scan_folder(folder):
        LOG.info("Scanning %r" % (folder))
        print("Scanning %r" % (folder))
        spinner_position = 0
        stdout.write( "Counting... /" )
        count_total = 0
        for root, dirs, files in walk(folder):
            for file in files:
                if not any([file.endswith(_) for _ in EXTS]):
                    continue
                spinner_position = (spinner_position + 1) % len(spinner_chars)
                stdout.write( "\b%s" % spinner_chars[spinner_position] )
                stdout.flush()
            count_total += len(files)
        stdout.write("\b ")
        stdout.flush()
        stdout.write( "\n%d files to examine\n" % count_total )

        pb = ProgressBar(tc, "Scanning...")

        count_scanned = 0
        count_processed = 0
        completed_ratio = 0.0
        for root, dirs, files in walk(folder):
            for file in files:
                if not any([file.endswith(_) for _ in EXTS]):
                    continue
                try:
                    process(path.join(root, file))
                    count_scanned += 1
                    count_processed += 1
                    completed_ratio = float(count_processed) / float(count_total)
                except TypeError as exc:
                    LOG.error('Unable to scan %s (%s)' % (
                            path.join(root, file), exc))
                pb.update(completed_ratio, path.join(root, file))
        pb.update(1.0, "done")
        stdout.write( "\n" )

    glob = subfolder.endswith('*')

    if glob:
        subfolder = subfolder[0:-1]
        candidates = [_ for _ in listdir(top) if _.startswith(subfolder)]
        for subfolder in candidates:
            scan_folder(path.join(top, subfolder))
    else:
        scan_folder(path.join(top, subfolder))
