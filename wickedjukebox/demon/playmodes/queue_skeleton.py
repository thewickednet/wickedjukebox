# pylint: disable=invalid-name
#
# TODO This requires some names to be camel-case. This should be removed in the
# future, but then the "player" API must change as well.

# pylint: disable=unused-argument
#
# This is a "skeleton" file with empty implementations. Arguments are always
# unused.
"""
This is a no-op playmode used as blueprint for new playmodes.
Simply complete the methods in this module and make them return the right type
and you should be fine.
"""

#
# These imports might prove useful:
#
## from wickedjukebox.demon.model import create_session, Song
## from wickedjukebox.demon.model import create_session, QueueItem


def enqueue(session, songID, userID, channelID):
    """
    Enqueues a song onto a queue of a given channel

    @type  session: Session
    @param session: The DB Session

    @type  songID: int
    @param songID: The id of the song to be enqueued

    @type  channelID: int
    @param channelID: The id of the channel

    @type  userID: int
    @param userID: The user who added the queue action
    """

    pass


def dequeue(session, channelID):
    """
    Return the next song from the queue

    @type  session: Session
    @param session: The DB Session

    @type  channelID: int
    @param channelID: The id of the channel

    @rtype:  Song
    @return: This should return a valid "Song" instance, which points to the next song
             on the queue.
             If nothing was on the queue, or no song could be determnined, then return
             "None", so the system can fall back to random mode.
    """

    return None


def moveup(session, channelID, qid, delta):
    """
    Move a song upwards in the queue by <delta> steps
    (meaning it will be played earlier).

    @type  session: Session
    @param session: The DB Session

    @type channelID: int
    @param channelID: The channel ID

    @type  delta: int
    @param delta: How many steps the song is move up in the queue

    @type  qid: int
    @param qid: The database ID of the queue item (*not* the song!)
    """
    pass


def movedown(session, channelID, qid, delta):
    """
    Move a song downwards in the queue by <delta> steps
    (meaning it will be played later).

    @type  session: Session
    @param session: The DB Session

    @type channelID: int
    @param channelID: The channel ID

    @type  delta: int
    @param delta: How many steps the song is move down in the queue

    @type  qid: int
    @param qid: The database ID of the queue item (*not* the song!)
    """
    pass


def movetop(session, channelID, qid):
    """
    Move a song to the top of the queue (meaning it will be played next)

    @type  session: Session
    @param session: The DB Session

    @type channelID: int
    @param channelID: The channel ID

    @type  qid: int
    @param qid: The database ID of the queue item (*not* the song!)
    """
    pass


def movebottom(session, channelID, qid):
    """
    Move a song to the bottom of the queue (meaning it will be played last)

    @type  session: Session
    @param session: The DB Session

    @type channelID: int
    @param channelID: The channel ID

    @type  qid: int
    @param qid: The database ID of the queue item (*not* the song!)
    """
    pass


def list(session, channelID):
    """
    Returns an ordered list of the items on the queue including position.

    Example return value:

        [{
          'position': 1,
          'song': {
                'id':       123,
                'title':    'supercool song'
                'duration': 310
             },
          'album': {
                'id':   234,
                'name': 'My Album'
             },
          'artist': {
                'id':   345,
                'name': 'Wildecker Herzbuben'
             }
        }]

    @type  session: Session
    @param session: The DB Session

    @type channelID: int
    @param channelID: The channel ID

    @rtype: dict
    """
    pass
