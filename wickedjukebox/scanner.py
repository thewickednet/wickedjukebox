# pylint: disable=missing-docstring
"""
Audio file scanner module

This module contains everything needed to scan a directory of audio files an
store the metadata in the jukebox database
"""


import logging
import sys
from os import listdir, path, walk
from sys import stdout
from typing import TextIO
from progress.bar import ChargingBar

from sqlalchemy.sql import select
from wickedjukebox.demon.dbmodel import Session, Setting, Song, songTable

LOG = logging.getLogger(__name__)



def is_valid_audio_file(filename: str) -> bool:
    value = Setting.get(None, "recognizedTypes", default="").strip()
    if not value:
        return False
    exts = value.split(" ")
    return filename.endswith(exts[0])


def process(localpath: str) -> None:
    exts = Setting.get(None, "recognizedTypes", default="").split(" ")

    if not localpath:
        LOG.warning("Skipping undefined filename!")
        return

    session = Session()

    if is_valid_audio_file(localpath):
        try:
            song = Song.by_filename(session, localpath)
            if not song:
                song = Song(localpath, None, None)
            song.scan_from_file(localpath, sys.getfilesystemencoding())
            session.add(song)
            LOG.info(repr(song))
        except UnicodeDecodeError as exc:
            LOG.error("Unable to decode %r (%s)", localpath, exc)
        except KeyError as exc:
            LOG.error("Key Error: %s", exc)
    else:
        LOG.debug("%r is not a valid audio-file "
                  "(only scanning extensions %r)", localpath, exts)

    session.commit()
    session.close()


def do_housekeeping():
    """
    Database cleanup, and set other values that are difficult to read during
    scanning.
    """
    LOG.info("Performing housekeeping. This may take a while!")
    songs = select([songTable.c.localpath]).execute()
    for row in songs:
        try:
            if not path.exists(row[0]):
                print("%r removed from disk" % row[0])
        except UnicodeEncodeError as exc:
            LOG.error("Unable to decode %r (%s)", row[0], exc)

def count_files(folder: str, stream: TextIO = stdout) -> None:
    spinner_chars = r"/-\|"
    LOG.info("Scanning %r", folder)
    print("Scanning %r" % folder)
    spinner_position = 0
    stream.write("Counting... /")
    count_total = 0
    for _, _, files in walk(folder):
        for file in files:
            if not is_valid_audio_file(file):
                continue
            spinner_position = (spinner_position + 1) % len(spinner_chars)
            stream.write("\b%s" % spinner_chars[spinner_position])
            stream.flush()
        count_total += len(files)
    stream.write("\b ")
    stream.flush()
    stream.write("\n%d files to examine\n" % count_total)
    process_recursive(folder, count_total, stream)


def process_recursive(folder: str, total_files: int, stream: TextIO = stdout) -> None:
    pbar = ChargingBar("Scanning...", max=total_files)
    count_scanned = 0
    count_processed = 0
    for root, _, files in walk(folder):
        for file in files:
            if not is_valid_audio_file(file):
                continue
            try:
                process(path.join(root, file))
                count_scanned += 1
                count_processed += 1
            except TypeError as exc:
                LOG.error('Unable to scan %s (%s)',
                            path.join(root, file), exc)
            pbar.next()
    pbar.finish()
    stream.write("\n")

def scan(top: str, subfolder: str="") -> None:
    """
    Scans a folder rootet at <top> for audio files. It will scan the supfolder
    named in ``subfolder``. The "*" character can be used for globbing.

    @param top: The root folder to scan
    @param subfolder: The subfolder to scan.
    """

    glob = subfolder.endswith('*')

    if glob:
        subfolder = subfolder[0:-1]
        candidates = [_ for _ in listdir(top) if _.startswith(subfolder)]
        for candidate in candidates:
            count_files(path.join(top, candidate))
    else:
        count_files(path.join(top, subfolder))
