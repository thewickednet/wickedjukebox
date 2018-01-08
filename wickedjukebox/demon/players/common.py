STATUS_PAUSED = 'paused'
STATUS_STARTED = 'started'
STATUS_STOPPED = 'stopped'


def make_player(backend, id_, params):
    if backend == 'icecast':
        from wickedjukebox.demon.players.icecast import Player
        return Player(id_, params)
    elif backend == 'mpd':
        from wickedjukebox.demon.players.mpd import Player
        return Player(id_, params)
    else:
        raise ValueError('Unsupported backend: %r' % backend)
