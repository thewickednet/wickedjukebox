import wickedjukebox.scanner as scanner
from unittest.mock import Mock, patch
import pytest
from io import StringIO


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("filename.mp3", True),
        ("filename.txt", False),
    ],
)
def test_is_valid_file(filename: str, expected: bool):
    with patch("wickedjukebox.scanner.Setting") as Setting:
        Setting.get.return_value = ".mp3"
        result = scanner.is_valid_audio_file(filename)
        assert result == expected


@pytest.mark.parametrize(
    "value",
    ["", "  "],
)
def test_is_valid_file_empty_settings(value):
    with patch("wickedjukebox.scanner.Setting") as Setting:
        Setting.get.return_value = value
        result = scanner.is_valid_audio_file("foo.mp3")
        assert result == False


def test_process():
    """
    Scanning a song from a file should be called if the song exists in the
    database
    """
    with patch("wickedjukebox.scanner.Song.by_filename") as by_filename, patch(
        "wickedjukebox.scanner.Session"
    ), patch("wickedjukebox.scanner.Setting") as Setting:
        Setting.get.return_value = ".mp3"
        song = Mock(localpath="/path/to/mp3s/file.mp3")
        by_filename.return_value = song
        result = scanner.process("/path/to/mp3s/file.mp3")
        song.scan_from_file.assert_called_with(
            "/path/to/mp3s/file.mp3", "utf-8"
        )


def test_process_new():
    """
    Scanning a song from a file should be called if the song does not exist in
    the database
    """
    with patch("wickedjukebox.scanner.Song") as Song, patch(
        "wickedjukebox.scanner.Session"
    ), patch("wickedjukebox.scanner.Setting") as Setting:
        Setting.get.return_value = ".mp3"
        song = Mock(localpath="/path/to/mp3s/file.mp3")
        Song.by_filename.return_value = None
        Song.return_value = song
        scanner.process("/path/to/mp3s/file.mp3")
        song.scan_from_file.assert_called_with(
            "/path/to/mp3s/file.mp3", "utf-8"
        )


def test_process_empty_filename():
    """
    Calling a scan with empty argument should not crash the system (shoule be a
    no-op)
    """
    with patch("wickedjukebox.scanner.Setting"):
        scanner.process("")


@pytest.mark.parametrize(
    "error", [UnicodeDecodeError("utf8", b"x", 1, 2, "reason"), KeyError()]
)
def test_process_errors(error):
    """
    Some errors should not crash out
    """
    with patch("wickedjukebox.scanner.Song") as Song, patch(
        "wickedjukebox.scanner.Session"
    ), patch("wickedjukebox.scanner.Setting") as Setting:
        Setting.get.return_value = ".mp3"
        Song.by_filename.side_effect = error
        scanner.process("/path/to/mp3s/file.mp3")


def test_process_invalid_file():
    """
    Scanning a non-supported file should be a no-op
    """
    with patch("wickedjukebox.scanner.Song") as Song, patch(
        "wickedjukebox.scanner.Session"
    ), patch("wickedjukebox.scanner.Setting") as Setting:
        Setting.get.return_value = ".mp3"
        scanner.process("/path/to/mp3s/file.txt")


def test_housekeeping():
    with patch("wickedjukebox.scanner.select") as select, patch(
        "wickedjukebox.scanner.path"
    ) as path:
        select().execute.return_value = ["file1.mp3", "file2.mp3"]
        path.exists.side_effect = [True, False]
        scanner.do_housekeeping()


def test_count_files():
    data = StringIO()
    with patch("wickedjukebox.scanner.walk") as walk, patch(
        "wickedjukebox.scanner.is_valid_audio_file"
    ) as iva, patch("wickedjukebox.scanner.process_recursive"):
        iva.side_effect = [True, False]
        walk.return_value = [("/path/to/mp3s", [], ["file1.mp3", "file2.txt"])]
        scanner.count_files("/path/to/mp3s", data)
    output = data.getvalue()
    assert "2 files" in output


def test_process_recursive():
    data = StringIO()
    with patch("wickedjukebox.scanner.walk") as walk, patch(
        "wickedjukebox.scanner.is_valid_audio_file"
    ) as iva, patch("wickedjukebox.scanner.process"):
        iva.side_effect = [True, False]
        walk.return_value = [("/path/to/mp3s", [], ["file1.mp3", "file2.txt"])]
        scanner.process_recursive("/path/to/mp3s", 2, data)


def test_scan():
    with patch("wickedjukebox.scanner.listdir") as listdir, patch(
        "wickedjukebox.scanner.count_files"
    ) as cntf:
        listdir.return_value = ["/path/to/mp3s/a", "/path/to/something/else"]
        scanner.scan("/path/to/mp3s", "a")
        cntf.assert_called_with("/path/to/mp3s/a")


def test_scan_glob():
    with patch("wickedjukebox.scanner.listdir") as listdir, patch(
        "wickedjukebox.scanner.count_files"
    ) as cntf:
        listdir.return_value = ["a"]
        scanner.scan("/path/to/mp3s", "a*")
        cntf.assert_called_with("/path/to/mp3s/a")
