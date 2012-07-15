"""
Audio file scanner module

This module contains everything needed to scan a directory of audio files an
store the metadata in the jukebox database
"""
from os import walk, path, sep
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


def process(localpath, encoding):

    if localpath is None or encoding is None:
        LOG.warning( "Skipping undefined filename!" )
        return

    session = Session()

    if is_valid_audio_file(localpath):
        try:
            song = session.query(Song).filter_by( localpath=localpath ).first()
            if not song:
                song = Song(localpath, None, None)
            song.scan_from_file( localpath, encoding )
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

def scan(top, capping=u""):
    """
    Scans a folder rootet at <top> for audio files. It will only include files
    starting with <capping>

    @param top: The root folder to scan
    @param capping: Only scan top-level folders starting with this string
    """
    from sys import stdout

    top = fsencode(top)
    capping = fsencode(capping)

    # if the capping ends with a path separator, then directly dive into that
    # directory
    if capping.endswith(sep):
        top = path.join(top, *capping.split(sep))
        capping = u""

    LOG.info("Starting scan on %r with capping %r" % (top, capping))

    spinner_chars = r"/-\|"
    spinner_position = 0
    stdout.write( "Counting... /" )
    count_total = 0
    for root, dirs, files in walk(fsencode(top)):
        for file in files:
            spinner_position = (spinner_position + 1) % len(spinner_chars)
            stdout.write( "\b%s" % spinner_chars[spinner_position] )
            stdout.flush()
        count_total += len(files)
    stdout.write("\b ")
    stdout.flush()

    stdout.write( "\n%d files to examine\n" % count_total )

    count_scanned = 0
    count_processed = 0
    completed_ratio = 0.0
    stdout.write( "[%50s]" % " " )
    for root, dirs, files in walk(fsencode(top)):
        relative_path = root[len(top)+1:]
        for file in files:
            stat_char = "."
            if path.join(relative_path, file).startswith(fsencode(capping)):
                process( *fsdecode( path.join(root, file) ) )
                stat_char = "#"
                count_scanned += 1
            count_processed += 1
            completed_ratio = float(count_processed) / float(count_total)
            progress_chars = int( 50*completed_ratio )*stat_char
            stdout.write( 51*"\b" + "%-50s]" % progress_chars )
    stdout.write( "\n" )
            
    LOG.info( "Scanned %d songs" % count_scanned )

