# pylint: disable=missing-docstring
"""
Audio file scanner module

This module contains everything needed to scan a directory of audio files an
store the metadata in the jukebox database
"""


import logging
from pathlib import Path
from sys import stdout
from typing import List, TextIO

from progress.bar import ChargingBar
from sqlalchemy.orm import Session as TSession

from wickedjukebox.demon.dbmodel import Session, Song

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


def process_files(files: List[Path], stream: TextIO = stdout) -> None:
    pbar = ChargingBar(
        "Scanning: ", max=len(files)
    )  # TODO use something more moden
    for file in files:
        try:
            process(file)
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
