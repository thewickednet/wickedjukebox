"""
Audio file scanner module

This module contains everything needed to scan a directory of audio files an
store the metadata in the jukebox database
"""
from os import walk, path, sep
import logging
from demon.dbmodel import Song, songTable, Session, Setting
from sqlalchemy.sql import select
logger = logging.getLogger(__name__)

valid_extensions = Setting.get("recognizedTypes").split(" ")

def is_valid_audio_file(path):
    return path.endswith(valid_extensions[0])

def process(localpath):
    if not localpath:
       logger.warning( "Skipping undefined filename!" )
       return

    session = Session()

    if is_valid_audio_file(localpath):
       song = session.query(Song).filter_by(localpath=localpath).first()
       if not song:
          song = Song(localpath, None, None)
       song.scan_from_file(localpath)
       session.add(song)
       logger.info( "%r" % (song) )
    else:
       logger.debug("%r is not a valid audio-file (only scanning extensions %r)" % (localpath, valid_extensions))

    session.commit()
    session.close()

def do_housekeeping():
    """
    Database cleanup, and set other values that are difficult to read during scanning
    """
    logger.info( "Performing housekeeping. This may take a while!" )
    songs = select([songTable.c.localpath]).execute()
    for row in songs:
       if not path.exists(row[0]):
           print `row[0]`, "removed from disk (No action taken!)"

def filter_capping(root, filename, capping):
    relative_path = filename[len(root)+1:]
    return not relative_path.startswith(capping)

def filter_valid_extenstion(root, filename):
    extinfo = path.splitext(filename)
    if not extinfo:
       logger.warn("Unable to split extension from file %r. This file will be ignored!" % filename )
       return True
    else:
       extension = extinfo[1].replace(".", "")
       if extension not in valid_extensions:
          logger.info("%r is not a valid audio-file (only scanning extensions %r)" % (filename, valid_extensions))
          return True
    return False

def processor_todatabase(root, localpath):
    session = Session()
    song = session.query(Song).filter_by(localpath=localpath).first()
    if not song:
       song = Song(localpath, None, None)
    song.scan_from_file(localpath)
    session.add(song)
    logger.debug( "%r at %r" % (song, localpath) )
    session.commit()
    session.close()

def scan(top, capping=u""):
    """
    Scans a folder rootet at <top> for audio files. It will only include files starting with <capping>

    @param top: The root folder to scan
    @param capping: Only scan top-level folders starting with this string
    """
    from sys import stdout

    # if the capping ends with a path separator, then directly dive into that
    # directory
    if capping.endswith(sep):
       top = path.join(top, *capping.split(sep))
       capping = u""

    logger.info("Starting scan on %r with capping %r" % (top, capping))

    spinner_chars = r"/-\|"
    spinner_position = 0
    stdout.write( "Counting... /" )
    count_total = 0
    for root, dirs, files in walk(top):
       for file in files:
          spinner_position = (spinner_position + 1) % len(spinner_chars)
          stdout.write( "\b%s" % spinner_chars[spinner_position] )
          stdout.flush()
       count_total += len(files)

    stdout.write( "\n%d files to examine\n" % count_total )

    count_scanned = 0
    count_processed = 0
    completed_ratio = 0.0
    stdout.write( "[%50s]" % " " )
    for root, dirs, files in walk(top):
       relative_path = root[len(top)+1:]
       for file in files:
          stat_char = "."
          if path.join(relative_path, file).startswith(capping):
             process(*path.join(root, file))
             stat_char = "#"
             count_scanned += 1
          count_processed += 1
          completed_ratio = float(count_processed) / float(count_total)
          progress_chars = int( 50*completed_ratio )*stat_char
          stdout.write( 51*"\b" + "%-50s]" % progress_chars )
    stdout.write( "\n" )

    logger.info( "Scanned %d songs" % count_scanned )

