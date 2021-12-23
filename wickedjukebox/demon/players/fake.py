# pylint: disable=unused-argument
from typing import Generator
from wickedjukebox.demon.dbmodel import Song


class Player(object):
    def __init__(self, id_, params, sys_utctime=0):
        pass

    @property
    def connection(self):
        pass

    def connect(self):
        pass

    def disconnect(self):
        pass

    def queue(self, filename):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def crop_playlist(self, length=2):
        pass

    def listeners(self):  # pylint: disable=no-self-use
        pass

    def current_song(self):
        pass

    def pause(self):
        pass

    def position(self):
        pass

    def skip(self):
        pass

    def status(self) -> str:
        pass

    def upcoming_songs(self) -> Generator[Song, None, None]:
        return []

    def playlistPosition(self) -> int:
        pass

    def playlistSize(self) -> int:
        pass

    def clearPlaylist(self) -> None:
        pass

    def updatePlaylist(self) -> None:
        pass
