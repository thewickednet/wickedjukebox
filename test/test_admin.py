"""
Unit-test for the command-line admin interface
"""
# pylint: disable=redefined-outer-name

from typing import List
from unittest.mock import Mock, patch

import pytest

import wickedjukebox.cli.jukebox_admin as admin

TEST_SETTINGS = {
    "mediadir": "fake-mediadir",
}


@pytest.fixture
def cmd():
    """
    This ficture prepares and returns a "CMD" instance (from the Python "cmd"
    module).
    """
    with patch("wickedjukebox.cli.jukebox_admin.Terminal"):
        cmd = admin.Console()
        yield cmd


def test_color_prompt():
    """
    Ensure the terminal colors are properly set
    """
    term = Mock()
    term.blue = "<blue>"
    term.normal = "<normal>"
    result = admin.colorprompt(term, "blue", "label")
    assert result == "<blue>               label<normal> "


def test_quit(cmd: admin.Console):
    """
    Quitting should give us an exit-code of 1
    """
    result = cmd.do_quit("")
    assert result == 1


@pytest.mark.parametrize(
    "path",
    [
        [],
        ["foo"],
        ["foo", "bar"],
    ],
)
def test_ls(cmd: admin.Console, path: List[str]):
    """
    Listing entries should work
    """
    for item in path:
        cmd.do_cd(item)
    mod = "wickedjukebox.cli.jukebox_admin"
    with patch(f"{mod}.get_artists") as artists, patch(
        f"{mod}.get_albums"
    ) as albums, patch(f"{mod}.get_songs") as songs:
        artists.return_value = [Mock(name="fake-artist")]
        albums.return_value = [Mock(name="fake-album")]
        songs.return_value = [Mock(title="fake-song")]
        cmd.do_ls("fake-line")
