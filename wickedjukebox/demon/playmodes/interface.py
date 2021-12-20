from abc import ABCMeta, abstractmethod
from typing import List, NamedTuple, Optional

from wickedjukebox.demon.dbmodel import Song

RandomItem = NamedTuple('RandomItem', [
    ('song', Song),
    ('stats', dict),
])


class PlayMode(metaclass=ABCMeta):

    @abstractmethod
    def bootstrap(self) -> None:
        """
        This is always called as soon as the class is loaded.

        Note that this will be called on each iteration, so it should cope with
        that. If you want to process this method only once you should deal with
        that internally (by using a sentinel variable for example).
        """
        raise NotImplementedError()

    @abstractmethod
    def get(self) -> Optional[Song]:
        """
        Returns a random song.

        .. note::
            This method should *always* return a valid Song instance. Only
            return "None" if something went seriously wrong.
        """
        raise NotImplementedError()

    @abstractmethod
    def prefetch(self, blocking: bool = False) -> None:
        """
        Trigger prefetching of a song. This may be used when a client requests
        that the song marked as "upcoming song" is unwanted.

        Playmodes that do not support a lookahead (see also "peek") will simply
        do nothing when this method is called.

        :param blocking: Whether to run the internal prefetch call
            asynchronously or not. This MUST be implemented for asynchronous
            prefetchers to ensure thread safety
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_candidates(self) -> List[RandomItem]:
        raise NotImplementedError()

    @abstractmethod
    def test(self) -> List[RandomItem]:
        """
        Used to run a test on the random mode. This should return a list of
        tuples containing a Song instance as first element, and a dictionary of
        stats as second element.

        :return: List of RandomItem instances
        """
        raise NotImplementedError()
