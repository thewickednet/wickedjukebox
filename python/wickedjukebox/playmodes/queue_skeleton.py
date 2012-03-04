"""
This is a no-op playmode used as blueprint for new playmodes.
Simply complete the methods in this module and make them return the right type
and you should be fine.
"""

#
# These imports might prove useful:
#
## from demon.model import create_session, Song
## from demon.model import create_session, QueueItem

def enqueue(song_id, user_id, channel_id):
    """
    Enqueues a song onto a queue of a given channel

    @type  song_id: int
    @param song_id: The id of the song to be enqueued

    @type  channel_id: int
    @param channel_id: The id of the channel

    @type  user_id: int
    @param user_id: The user who added the queue action
    """

    # pylint: disable=W0613
    pass

def dequeue( channel_id ):
    """
    Return the next song from the queue

    @type  channel_id: int
    @param channel_id: The id of the channel

    @rtype:  Song
    @return: This should return a valid "Song" instance, which points to the next song
                on the queue.
                If nothing was on the queue, or no song could be determnined, then return
                "None", so the system can fall back to random mode.
    """

    # pylint: disable=W0613
    return None

def moveup( channel_id, qid, delta ):
    """
    Move a song upwards in the queue by <delta> steps
    (meaning it will be played earlier).

    @type channel_id: int
    @param channel_id: The channel ID

    @type  delta: int
    @param delta: How many steps the song is move up in the queue

    @type  qid: int
    @param qid: The database ID of the queue item (*not* the song!)
    """
    # pylint: disable=W0613
    pass

def movedown( channel_id, qid, delta):
    """
    Move a song downwards in the queue by <delta> steps
    (meaning it will be played later).

    @type channel_id: int
    @param channel_id: The channel ID

    @type  delta: int
    @param delta: How many steps the song is move down in the queue

    @type  qid: int
    @param qid: The database ID of the queue item (*not* the song!)
    """
    # pylint: disable=W0613
    pass

def movetop( channel_id, qid ):
    """
    Move a song to the top of the queue (meaning it will be played next)

    @type channel_id: int
    @param channel_id: The channel ID

    @type  qid: int
    @param qid: The database ID of the queue item (*not* the song!)
    """
    # pylint: disable=W0613
    pass

def movebottom( channel_id, qid ):
    """
    Move a song to the bottom of the queue (meaning it will be played last)

    @type channel_id: int
    @param channel_id: The channel ID

    @type  qid: int
    @param qid: The database ID of the queue item (*not* the song!)
    """
    # pylint: disable=W0613
    pass

def list( channel_id ):
    """
    Returns an ordered list of the items on the queue including position.

    Example return value:

         [{
            'position': 1,
            'song': {
                    'id':         123,
                    'title':     'supercool song'
                    'duration': 310
                },
            'album': {
                    'id':    234,
                    'name': 'My Album'
                },
            'artist': {
                    'id':    345,
                    'name': 'Wildecker Herzbuben'
                }
         }]

    @type channel_id: int
    @param channel_id: The channel ID

    @rtype: dict
    """
    # pylint: disable=W0613
    pass
