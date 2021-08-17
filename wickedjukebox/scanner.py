# pylint: disable=missing-docstring
"""
Audio file scanner module

This module contains everything needed to scan a directory of audio files an
store the metadata in the jukebox database
"""


import logging
from os import path
from pathlib import Path
from sys import stdout
from typing import List, TextIO

from progress.bar import ChargingBar
from sqlalchemy.orm import Session as TSession
from sqlalchemy.sql import select

from wickedjukebox.demon.dbmodel import Session, Song, songTable

LOG = logging.getLogger(__name__)
SUPPORTED_FILETYPES = {".mp3"}


def is_valid_audio_file(filename: Path) -> bool:
    checks = [filename.name.endswith(ext) for ext in SUPPORTED_FILETYPES]
    return any(checks)


def process(pth: Path) -> None:
    if not is_valid_audio_file(pth):
        return
    session: TSession = Session()
    song = Song.by_filename(session, str(pth))
    if not song:
        song = Song(str(pth))
    song.update_metadata()
    session.merge(song)
    LOG.info(repr(song))
    session.commit()
    session.close()
    return


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


def process_files(files: List[Path], stream: TextIO = stdout) -> None:
    pbar = ChargingBar(
        "Scanning: ", max=len(files)
    )  # TODO use something more moden
    count_scanned = 0
    count_processed = 0
    for file in files:
        try:
            process(file)
            count_scanned += 1
            count_processed += 1
        except TypeError as exc:
            LOG.error("Unable to scan %s (%s)", file, exc, exc_info=True)
        pbar.next()
    pbar.finish()
    stream.write("\n")


def collect_files(path: Path, stream: TextIO = stdout) -> List[Path]:
    """
    Generate a list of valid audio-files.

    :param path: The root folder to scan
    :param stream: The stream onto which to write the progress info
    """

    LOG.info("Scanning %r", path)
    print(f"Looking for audio-files in: {path}")
    stream.write(" └ 0 audio files found...")
    output: List[Path] = []
    for file in path.glob("**/*"):
        if not is_valid_audio_file(file):
            continue
        stream.write("\r └ %d audio files found..." % len(output))
        stream.flush()
        output.append(file)
    stream.write("\r  └ %d audio files found   \n" % len(output))
    stream.flush()
    return output


def scan(path: str, stream: TextIO = stdout) -> None:
    audiofiles = collect_files(Path(path), stream)
    process_files(audiofiles, stream)
