# pylint: disable=redefined-outer-name
"""
This file contains test to verify the construction of the various modular
jukebox components.
"""
from configparser import ConfigParser
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest

import wickedjukebox.component as comp
from wickedjukebox.component.player import MpdPlayer, NullPlayer
from wickedjukebox.component.random import (
    AllFilesRandom,
    NullRandom,
    SmartPrefetch,
)
from wickedjukebox.config import Config


@pytest.fixture
def fake_config() -> Generator[Config, None, None]:
    """
    A ficture to provide a fake config for the application
    """
    config = Config()
    config.config = ConfigParser()
    yield config


def test_get_autoplay(fake_config: Config):
    """
    Without config we should get a null-instance
    """
    fake_config.config.read_string(  # type: ignore
        """
        [channel:test-channel:autoplay]
        backend = null
        """
    )
    player = comp.get_autoplay(fake_config, "test-channel")
    assert isinstance(player, NullRandom)


def test_get_autoplay_afr(fake_config: Config):
    """
    We should be able to construct the allfiles-random mode
    """
    fake_config.config.read_string(  # type: ignore
        """
        [channel:test-channel:autoplay]
        type = allfiles_random
        root = example
        """
    )
    player = comp.get_autoplay(fake_config, "test-channel")
    assert isinstance(player, AllFilesRandom)
    assert player.root == "example"


def test_get_autoplay_smart(fake_config: Config):
    """
    We should be able to construct the smart-random mode
    """
    fake_config.config.read_string(  # type: ignore
        """
        [database]
        dsn = sqlite://

        [channel:test-channel:autoplay]
        type = smart_prefetch
        """
    )
    with patch("wickedjukebox.component.random.SmartPrefetchThread"):
        player = comp.get_autoplay(fake_config, "test-channel")
    assert isinstance(player, SmartPrefetch)


def test_get_player(fake_config: Config):
    """
    Without config we should get a null-instance
    """
    fake_config.config.read_string(  # type: ignore
        """
        [channel:test-channel:player]
        backend = null
        """
    )
    player = comp.get_player(fake_config, "test-channel")
    assert isinstance(player, NullPlayer)


def test_get_player_mpd(fake_config: Config):
    """
    If the jukebox is configured to use mpd as backend we should get an
    appropriate player
    """
    fake_config.config.read_string(  # type: ignore
        """
        [channel:test-channel:player]
        backend = mpd
        host = 127.0.0.1
        port = 6600
        path_map = local_path:container_path
        """
    )
    player = comp.get_player(fake_config, "test-channel")
    assert isinstance(player, MpdPlayer)
    assert player.host == "127.0.0.1"
    assert player.port == 6600
    assert player.path_map.jukebox_path == Path("local_path")
    assert player.path_map.mpd_path == Path("container_path")
