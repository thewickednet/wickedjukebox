#!/usr/bin/python
# -*- coding: utf-8 -*-

# pylint: disable=global-statement
#
# Use of the global statement is currently required as this module behaves like
# a singleton.
"""
Weighed random. Different factors are considered when selecting a song at
random. Like the time it was last played, how often it was skipped, and so on.
"""
import logging
import threading
from typing import Generator, Optional
from sqlalchemy.orm.strategy_options import load_only

from sqlalchemy.sql import func, select
from sqlalchemy.sql import text as dbText
import sqlalchemy.orm as orm
from sqlalchemy.sql.elements import literal_column, not_
from sqlalchemy.sql.expression import and_, bindparam, text
from wickedjukebox.demon.dbmodel import (Session, Song, User, channelTable,
                                         songTable)
from wickedjukebox.config import Config, ConfigKeys
from wickedjukebox.smartplaylist.dbbridge import parse_dynamic_playlists
from . import queries

LOG = logging.getLogger(__name__)

ALREADY_INITIALISED = False

PREFETCH_STATE = {}


def bootstrap(channel_id):
    global ALREADY_INITIALISED

    if ALREADY_INITIALISED:
        return

    # as the query can take fscking long, we prefetch one song as soon as this
    # module is loaded!
    LOG.info('prefetching initial random song for each channel ...')
    query = select([channelTable.c.id, channelTable.c.name])
    query = query.where(channelTable.c.id == channel_id)
    row = query.execute().fetchone()
    pref = Prefetcher(row[0])
    pref.run()
    LOG.debug('  Channel %r prefetched %r', row[1], PREFETCH_STATE[row[0]])
    ALREADY_INITIALISED = True

def find_song(session: orm.Session, channel_name: str) -> Optional[Song]:
    # pylint: disable=too-many-statements, too-many-locals
    #
    # This may be difficult to refactorl The high count of statements and
    # locals comes partly from constructing the select-query and fetching
    # settings. Ignoring this warning for now.
    """
    determine a song that would be best to play next and return it
    """

    # setup song scoring coefficients
    user_rating = Config.get(
        ConfigKeys.SCORING_USERRATING,
        4,
        channel=channel_name,
        converter=int,
    )
    last_played = Config.get(
        ConfigKeys.SCORING_LASTPLAYED,
        10,
        channel=channel_name,
        converter=int,
    )
    song_age = Config.get(
        ConfigKeys.SCORING_SONGAGE,
        1,
        channel=channel_name,
        converter=int,
    )
    never_played = Config.get(
        ConfigKeys.SCORING_NEVERPLAYED,
        4,
        channel=channel_name,
        converter=int,
    )
    randomness = Config.get(
        ConfigKeys.SCORING_RANDOMNESS,
        1,
        channel=channel_name,
        converter=int
    )
    max_random_duration = Config.get(
        ConfigKeys.MAX_RANDOM_DURATION,
        600,
        channel=channel_name,
        converter=int,
    )
    proofoflife_timeout = Config.get(
        ConfigKeys.PROOFOFLIFE_TIMEOUT,
        120,
        converter=int
    )
    is_mysql = Config.get(ConfigKeys.DSN, "").lower().startswith("mysql")

    if is_mysql:

        query = session.query(User.id).filter(
            func.unix_timestamp(User.proof_of_listening)
            + proofoflife_timeout > func.unix_timestamp(func.now())
        )
        if query.count() == 0:
            # no users online
            query = queries.smart_random_no_users(
                never_played,
                last_played,
                song_age,
                randomness,
                max_random_duration,
            )
        else:
            query = queries.smart_random_with_users(
                never_played,
                user_rating,
                last_played,
                proofoflife_timeout,
                randomness,
                song_age,
                max_random_duration,
            )
    else:
        raise Exception(
            "SQLite support discontinued since revision 346. It may reappear in the future!")

    query = query.where(not_(text("s.broken")))  # type: ignore
    if PREFETCH_STATE and PREFETCH_STATE[channel_id]:
        LOG.info("Ignoring song %r from random selection as it was already "
                 "prefetched!",
                 PREFETCH_STATE[channel_id])
        query = query.where(text("s.id != :excluded_song").bindparams(excluded_song=PREFETCH_STATE[channel_id].id))  # type: ignore

    # TODO: Add dynamic playlist clauses
    # TODO fix cross-product issue query = query.where(and_(*parse_dynamic_playlists()))

    LOG.debug(query)
    res = session.execute(query)
    candidate = res.first()

    if candidate is None:
        return None

    try:
        if not candidate.score:
            # no users are online!
            session.close()
            return None
        out = (candidate.id, candidate.localpath, float(candidate.score))
        LOG.info("Selected song (%d, %s) via smartget. Score was %4.3f",
                 *out)
        selected_song = session.query(Song).filter(
            songTable.c.id == out[0]).first()
        session.close()
        return selected_song
    except IndexError:
        LOG.warning('No song returned from query. Is the database empty?',
                    exc_info=True)
        session.close()
        return None


class Prefetcher(threading.Thread):

    _channel_id = None

    def __init__(self, channel_id):
        threading.Thread.__init__(self)
        self._channel_id = channel_id

    def run(self):
        global PREFETCH_STATE
        LOG.debug("Background prefetching... ")
        session = Session()
        song = find_song(session, self._channel_id)
        LOG.debug("  ... prefetched %r", song)
        PREFETCH_STATE[self._channel_id] = song


def get(channel_id):
    pref = Prefetcher(channel_id)
    pref.start()

    # wait until a song is prefetched (in case two 'gets' are called quickly
    # after another)
    while not PREFETCH_STATE and not PREFETCH_STATE[channel_id]:
        pass

    return PREFETCH_STATE[channel_id]
