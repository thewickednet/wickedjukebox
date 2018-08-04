from sqlalchemy.orm import Session

from .interface import PlayMode
from .random_wr2 import RandomWR2


def create(modname: str, channel_id: int = 0, session: Session = None) -> PlayMode:
    if modname == 'random_wr2':
        instance = RandomWR2(session, channel_id)
        return instance
    raise ValueError('No such play-mode: %r' % modname)
