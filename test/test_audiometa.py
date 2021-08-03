from datetime import date
from io import StringIO
from unittest.mock import Mock, patch

import pytest

import wickedjukebox.model.audiometa as am


@pytest.fixture
def meta():
    class DictObj(dict):
        pass

    wrapped = DictObj(
        {
            "TDRC": Mock(text="2000-01-02", encoding=1),
            "TIT2": Mock(text="title", encoding=2),
            "TPE1": Mock(text="artist", encoding=3),
            "TRCK": Mock(text="1/10", encoding=0),
            "TALB": Mock(text="album", encoding=1),
            "TCON": Mock(text="genre", encoding=1),
        }
    )
    wrapped.info = Mock(length=100, bitrate=128)
    meta = am.MP3Meta(wrapped)
    return meta


def test_display_file():
    stdout = StringIO()
    with patch("wickedjukebox.model.audiometa.MetaFactory"):
        am.display_file("the-filename.mp3", stdout)
    assert "the-filename.mp3" in stdout.getvalue()


@pytest.mark.parametrize(
    "attrname",
    [
        "get_artist",
        "get_title",
        "get_release_date",
        "get_comment",
        "get_track_no",
        "get_total_tracks",
        "get_album",
        "get_duration",
        "get_bitrate",
    ],
)
def test_audiometa(attrname):
    class DictObj(dict):
        pass

    wrapped = DictObj(
        {
            "TDRC": Mock(text="2000-01-02", encoding=1),
            "TIT2": Mock(text="title", encoding=2),
            "TPE1": Mock(text="artist", encoding=3),
            "TRCK": Mock(text="1/10", encoding=0),
            "TALB": Mock(text="album", encoding=1),
            "TCON": Mock(text="genre", encoding=1),
        }
    )
    wrapped.info = Mock(length=100, bitrate=128)
    meta = am.AudioMeta(wrapped)
    func = getattr(meta, attrname)
    value = func()
    assert value == "Unimplemented meta-info"


@pytest.mark.parametrize(
    "attrname, expected",
    [
        ("get_artist", "artist"),
        ("get_title", "title"),
        ("get_release_date", date(2000, 1, 2)),
        ("get_comment", "Unimplemented meta-info"),
        ("get_track_no", 1),
        ("get_total_tracks", 10),
        ("get_album", "album"),
        ("get_duration", 100),
        ("get_genres", ["genre"]),
        ("get_bitrate", 128),
    ],
)
def test_mp3meta(meta, attrname, expected):
    func = getattr(meta, attrname)
    value = func()
    assert value == expected


def test_get_values(meta):
    result = sorted([repr(value) for value in meta.values()])
    expected = [
        "'Unimplemented meta-info'",
        "'album'",
        "'artist'",
        "'title'",
        "1",
        "10",
        "100",
        "128",
        "['genre']",
        "datetime.date(2000, 1, 2)",
    ]
    assert result == expected


def test_get_keys(meta):
    result = sorted([repr(value) for value in meta.keys()])
    expected = [
        "'album'",
        "'artist'",
        "'bitrate'",
        "'comment'",
        "'duration'",
        "'genres'",
        "'release_date'",
        "'title'",
        "'total_tracks'",
        "'track_no'",
    ]
    assert result == expected


def test_items(meta):
    expected = [
        (
            "album",
            "album",
        ),
        (
            "artist",
            "artist",
        ),
        (
            "bitrate",
            128,
        ),
        (
            "comment",
            "Unimplemented meta-info",
        ),
        (
            "duration",
            100,
        ),
        (
            "genres",
            ["genre"],
        ),
        (
            "release_date",
            date(2000, 1, 2),
        ),
        (
            "title",
            "title",
        ),
        (
            "total_tracks",
            10,
        ),
        ("track_no", 1),
    ]
    result = sorted([value for value in meta.items()])
    assert result == expected


def test_len(meta):
    result = len(meta)
    assert result == 10


def test_repr(meta):
    result = repr(meta)
    assert isinstance(result, str)


def test_main():
    stdout = StringIO()
    with patch("wickedjukebox.model.audiometa.display_file") as df:
        am.main(["executable_name", "filename.mp3"], stream=stdout)
    df.assert_called_once_with("filename.mp3", stream=stdout)


def test_main_errored():
    stdout = StringIO()
    with patch("wickedjukebox.model.audiometa.display_file") as df:
        am.main(["executable_name"], stream=stdout)
    assert df.call_count == 0
