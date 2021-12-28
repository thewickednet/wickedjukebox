"""
This module contains tests for the new (2021) random implementation
"""

from pathlib import Path
from unittest.mock import patch

import wickedjukebox.component.random as rnd


def test_repr():
    obj = rnd.NullRandom(None, "none")
    result = repr(obj)
    assert "NullRandom" in result


def test_null_random():
    obj = rnd.NullRandom(None, "none")
    result = obj.pick()
    assert result is not None
    assert result == ""


def test_allfiles():
    obj = rnd.AllFilesRandom(None, "channel-name")
    obj.root = "fakeroot"
    with patch("wickedjukebox.component.random.Path") as MockPath:
        MockPath().glob.return_value = [Path("foo")]
        result = obj.pick()
    assert result is not None
    assert str(result) == str(Path("foo").absolute())


def test_allfiles_empty():
    obj = rnd.AllFilesRandom(None, "channel-name")
    obj.root = "fakeroot"
    with patch("wickedjukebox.component.random.Path") as MockPath:
        MockPath().glob.return_value = []
        result = obj.pick()
    assert result == ""
