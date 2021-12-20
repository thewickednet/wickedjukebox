import wickedjukebox.scanner as scanner
from unittest.mock import Mock, patch
import pytest
from pathlib import Path
from io import StringIO


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("filename.mp3", True),
        ("filename.txt", False),
    ],
)
def test_is_valid_file(filename: str, expected: bool):
    result = scanner.is_valid_audio_file(Path(filename))
    assert result == expected


def test_process_new():
    """
    Scanning a song from a file should be called if the song does not exist in
    the database
    """
    with patch("wickedjukebox.scanner.Song") as Song, patch(
        "wickedjukebox.scanner.Session"
    ) as Session:
        song = Mock(localpath="/path/to/mp3s/file.mp3")
        Song.by_filename.return_value = None  # type: ignore
        Song.return_value = song
        scanner.process(Path("/path/to/mp3s/file.mp3"))
        Song.by_filename.assert_called_with(  # type: ignore
            Session(), "/path/to/mp3s/file.mp3"
        )
        Song().update_metadata.assert_called_with()  # type: ignore


def test_process_empty_filename():
    """
    Calling a scan with empty argument should not crash the system (shoule be a
    no-op)
    """
    scanner.process(Path(""))


def test_process_invalid_file():
    """
    Scanning a non-supported file should be a no-op
    """
    with patch("wickedjukebox.scanner.Song") as Song, patch(
        "wickedjukebox.scanner.Session"
    ):
        scanner.process(Path("/path/to/mp3s/file.txt"))


def test_process_files(dbsession, transaction):
    stdout = StringIO()
    with patch("wickedjukebox.scanner.ChargingBar"), patch(
        "wickedjukebox.scanner.process"):
        scanner.process_files(["file1", "file2"], stdout)
