#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Weighed random. Different factors are considered when selecting a song at
random. Like the time it was last played, how often it was skipped, and so on.
"""
import logging
import threading

from sqlalchemy.sql import func, select
from sqlalchemy.sql import text as dbText
from wickedjukebox.demon.dbmodel import (Session, Setting, Song, channelTable,
                                         dynamicPLTable, engine, songTable,
                                         usersTable)
from wickedjukebox.demon.plparser import ParserSyntaxError, parseQuery
from wickedjukebox.demon.util import config

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
    s = select([channelTable.c.id, channelTable.c.name])
    s = s.where(channelTable.c.id == channel_id)
    row = s.execute().fetchone()
    pref = Prefetcher(row[0])
    pref.run()
    LOG.debug('  Channel %r prefetched %r', row[1], PREFETCH_STATE[row[0]])
    ALREADY_INITIALISED = True


def findSong(channel_id):
    """
    determine a song that would be best to play next and return it
    """
    global PREFETCH_STATE
    session = Session()

    # setup song scoring coefficients
    userRating = int(Setting.get(
        'scoring_userRating', 4,
        channel_id=channel_id))
    lastPlayed = int(Setting.get(
        'scoring_lastPlayed', 10,
        channel_id=channel_id))
    songAge = int(Setting.get(
        'scoring_songAge', 1,
        channel_id=channel_id))
    neverPlayed = int(Setting.get(
        'scoring_neverPlayed', 4,
        channel_id=channel_id))
    randomness = int(Setting.get(
        'scoring_randomness', 1,
        channel_id=channel_id))
    max_random_duration = int(Setting.get(
        'max_random_duration', 600,
        channel_id=channel_id))
    proofoflife_timeout = int(Setting.get('proofoflife_timeout', 120))

    whereClauses = ["NOT broken"]
    if PREFETCH_STATE and PREFETCH_STATE[channel_id]:
        LOG.info("Ignoring song %r from random selection as it was already "
                 "prefetched!",
                 PREFETCH_STATE[channel_id])
        whereClauses.append("s.id != %d" % PREFETCH_STATE[channel_id].id)

    # Retrieve dynamic playlists
    sel = select([dynamicPLTable.c.query])
    sel = sel.where(dynamicPLTable.c.group_id > 0)
    sel = sel.order_by('group_id')
    res = sel.execute().fetchall()
    for dpl in res:
        try:
            if parseQuery(dpl["query"]):
                whereClauses.append("(" + parseQuery(dpl["query"]) + ")")
            break  # only one query will be parsed. for now.... this is a big TODO
            # as it triggers an unexpected behaviour (bug). i.e.: Why the
            # heck does it only activate one playlist?!?
        except ParserSyntaxError as ex:
            import traceback
            traceback.print_exc()
            LOG.error(str(ex))
            LOG.error('Query was: %s', dpl.query)
        except:
            import traceback
            traceback.print_exc()
            LOG.error()

    if config['database.type'] == 'mysql':

        s = select([usersTable], func.unix_timestamp(
            usersTable.c.proof_of_listening) + proofoflife_timeout > func.unix_timestamp(func.now()))
        r = s.execute()
        if len(r.fetchall()) == 0:
            # no users online
            query = """
            SELECT s.id, s.localpath,
               ((IFNULL( least(604800, (NOW()-lastPlayed)), 604800)-604800)/604800*%(lastPlayed)d)
                  + IF( lastPlayed IS NULL, %(neverPlayed)d, 0)
                  + IFNULL( IF( (NOW()-s.added)<1209600, (NOW()-s.added)/1209600*%(songAge)d, 0), 0)
                  + ((RAND()*%(randomness)f*2)-%(randomness)f)
               AS score
            FROM song s
               LEFT JOIN channel_song_data c ON (c.song_id=s.id)
               INNER JOIN artist a ON ( a.id = s.artist_id )
               INNER JOIN album b ON ( b.id = s.album_id )
            WHERE (%(where)s) AND NOT s.broken AND s.duration < %(max_random_duration)d
            ORDER BY score DESC
            LIMIT 10 OFFSET 0
         """ % {
                'neverPlayed': neverPlayed,
                'userRating':  userRating,
                'lastPlayed':  lastPlayed,
                'songAge':     songAge,
                'randomness':  randomness,
                'max_random_duration': max_random_duration,
                'where':       ") AND (".join(whereClauses).replace("%", "%%"),
            }
        else:
            query = """
            SELECT s.id, s.localpath,
               ((IFNULL( least(604800, (NOW()-lastPlayed)), 604800)-604800)/604800*%(lastPlayed)d)
                  + ((IFNULL(ls.loves,0)) / (SELECT COUNT(*) FROM users WHERE UNIX_TIMESTAMP(proof_of_listening)+%(proofoflife)d > UNIX_TIMESTAMP(NOW())) * %(userRating)d)
                  + IF( lastPlayed IS NULL, %(neverPlayed)d, 0)
                  + IFNULL( IF( (NOW()-s.added) < 1209600, (NOW()-s.added)/1209600*%(songAge)d, 0), 0)
                  + ((RAND()*%(randomness)f*2)-%(randomness)f)
               AS score
            FROM song s
               LEFT JOIN channel_song_data c ON (c.song_id=s.id)
               LEFT JOIN (
                  SELECT song_id, COUNT(*) AS loves
                  FROM user_song_standing
                  INNER JOIN users ON(users.id=user_song_standing.user_id)
                  LEFT OUTER JOIN setting ON(users.id=setting.user_id AND setting.var="loves_affect_random")
                  WHERE standing='love' AND IFNULL(setting.value, 1) = 1
                     AND UNIX_TIMESTAMP(proof_of_listening)+%(proofoflife)d > UNIX_TIMESTAMP(NOW())
                  GROUP BY song_id
               ) ls ON (s.id=ls.song_id)
               LEFT JOIN (
                  SELECT song_id, COUNT(*) AS hates
                  FROM user_song_standing
                  INNER JOIN users ON(users.id=user_song_standing.user_id)
                  LEFT OUTER JOIN setting ON(users.id=setting.user_id AND setting.var="hates_affect_random")
                  WHERE standing='hate' AND IFNULL(setting.value, 1) = 1
                     AND UNIX_TIMESTAMP(proof_of_listening)+%(proofoflife)d > UNIX_TIMESTAMP(NOW())
                  GROUP BY song_id
               ) hs ON (s.id=hs.song_id)
               INNER JOIN artist a ON ( a.id = s.artist_id )
               INNER JOIN album b ON ( b.id = s.album_id )
            WHERE (%(where)s) AND IFNULL(hs.hates,0) = 0 AND NOT s.broken AND s.duration < %(max_random_duration)d
            ORDER BY score DESC
            LIMIT 10 OFFSET 0
         """ % {
                'neverPlayed': neverPlayed,
                'userRating':  userRating,
                'lastPlayed':  lastPlayed,
                'proofoflife': proofoflife_timeout,
                'randomness':  randomness,
                'songAge':     songAge,
                'max_random_duration': max_random_duration,
                'where':       ") AND (".join(whereClauses).replace("%", "%%"),
            }
    else:
        raise Exception(
            "SQLite support discontinued since revision 346. It may reappear in the future!")

    LOG.debug(query)
    resultProxy = dbText(query, bind=engine).execute()
    res = resultProxy.fetchall()

    if not res:
        return None

    try:
        if not res[0][2]:
            # no users are online!
            session.close()
            return None
        out = (res[0][0], res[0][1], float(res[0][2]))
        LOG.info("Selected song (%d, %s) via smartget. Score was %4.3f",
                 *out)
        selectedSong = session.query(Song).filter(
            songTable.c.id == out[0]).first()
        session.close()
        return selectedSong
    except IndexError:
        import traceback
        traceback.print_exc()
        LOG.warning('No song returned from query. Is the database empty?')
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
        song = findSong(self._channel_id)
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


def peek(channel_id):
    global PREFETCH_STATE
    output = PREFETCH_STATE.get(channel_id, None)
    if not output:
        return None
    return output, None


def prefetch(channel_id, async=True):
    global PREFETCH_STATE
    PREFETCH_STATE[channel_id] = None
    pref = Prefetcher(channel_id)
    if async:
        pref.start()
    else:
        pref.run()
