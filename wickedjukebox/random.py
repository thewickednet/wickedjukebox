from abc import ABC, abstractmethod

from wickedjukebox.adt import Song


class AbstractRandom(ABC):
    @abstractmethod
    def pick(self) -> Song:
        ...



class NullRandom(AbstractRandom):
    def pick(self) -> Song:
        return Song("", "", "", "")