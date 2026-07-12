"""
This module contains an entry point to run a "smart" query to find the next best
song taking channel statistics into account.
"""

import logging
import random
from enum import Enum
from typing import TYPE_CHECKING, Any, List, Mapping, Optional

import sqlalchemy.orm as orm
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import func
from sqlalchemy.sql.elements import not_
from sqlalchemy.sql.expression import and_, or_, text

from wickedjukebox.model.db.auth import User
from wickedjukebox.model.db.library import Song, UserSongStanding
from wickedjukebox.model.db.playback import Channel, DynamicPlaylist
from wickedjukebox.model.db.settings import Setting
from wickedjukebox.model.db.stats import ChannelStat

if TYPE_CHECKING:
    from typing import Tuple

LOG = logging.getLogger(__name__)

#: A song gains the maximum "last-played" score boost after this many seconds
LAST_PLAYED_CUTOFF = 7 * 24 * 60 * 60


class ScoringConfig(Enum):
    """
    Possible configuration values to influence the scoring query
    """

    USER_RATING = "user_rating"
    LAST_PLAYED = "last_played"
    NEVER_PLAYED = "never_played"
    RANDOMNESS = "randomness"
    MAX_DURATION = "max_duration"
    PROOF_OF_LIFE_TIMEOUT = "proof_of_life"
    #: 0 (or absent) = disabled (score the whole table). >0 = score only a
    #: random pool of this many candidate ids (fast, flat with library size).
    CANDIDATE_POOL_SIZE = "candidate_pool_size"


def get_standing_query(
    session,
    standing: str,
    setting_name: str,
    proofoflife_timeout: int,
) -> "Query[Any]":
    """
    Return a query retrieving the number of users that either "hate" or "love" a
    given song. Only users that have been listening within the last
    *proofoflife_timeout* seconds will be taken into account.
    """
    query = session.query(Song.id, func.count().label("count"))
    query = query.join(UserSongStanding)
    query = query.join(User)
    query = query.join(
        Setting,
        and_(
            Setting.var == setting_name,  # type: ignore
            User.id == Setting.user_id,  # type: ignore
        ),
        isouter=True,
    )
    query = query.filter(UserSongStanding.standing == standing)
    query = query.filter(func.ifnull(Setting.value, 1) == 1)  # type: ignore
    query = query.filter(
        func.unix_timestamp(User.proof_of_listening) + proofoflife_timeout
        > func.unix_timestamp(func.now())
    )
    query = query.group_by(UserSongStanding.song_id)
    return query


def score_expression(last_played: int, never_played: int, randomness: float):
    """
    Column-expression scoring a song without user statistics:
      - recency penalty (recently-played scores lower; never-played: no penalty)
      - never-played bonus
      - randomness
    """
    return (
        0
        - func.ifnull(
            ChannelStat.last_played_parametric(LAST_PLAYED_CUTOFF, last_played),
            0,
        )
        + func.if_(ChannelStat.lastPlayed.is_(None), never_played, 0)
        + ((func.rand() * randomness * 2) - randomness)
    )


def smart_random_no_users(
    session,
    never_played: int,
    last_played: int,
    randomness: float,
    max_random_duration: int,
):
    """
    Fetch a random song without taking any user-statistics into account. Only
    consider channel statistics.

    :param never_played: A score bonus for songs that have never been played.
    :param last_played: The maximum recency *penalty* applied to a just-played
        song, decaying linearly to 0 by ``LAST_PLAYED_CUTOFF`` (never-played
        songs incur no penalty).
    :randomness: A score modifier adding a dash of randomness to the overall
        score.
    :max_random_duration: Don't return songs with a longer duration than this
        value (in seconds).
    """

    query = (
        session.query(
            Song.id,
            Song.localpath,
            score_expression(last_played, never_played, randomness).label(
                "score"
            ),
        )
        .select_from(Song)
        .join(ChannelStat, isouter=True)
    )
    query = query.filter(Song.duration < max_random_duration)
    query = query.order_by(text("score DESC"))  # type: ignore
    return query  # type: ignore


def smart_random_with_users(
    session,
    never_played: int,
    user_rating: int,
    last_played: int,
    proofoflife_timeout: int,
    randomness: float,
    max_random_duration: int,
    num_active_users: int,
) -> "Query[Tuple[int, str, float]]":
    """
    Like :func:`smart_random_no_users`, but also factors in the ratings of
    currently-listening users: songs "loved" by active users get a score boost
    (``loves / num_active_users * user_rating``) and songs "hated" by any active
    user are filtered out. The base score is the same recency penalty +
    never-played bonus + randomness as the no-users variant.
    """

    loves_query = get_standing_query(
        session, "love", "loves_affect_random", proofoflife_timeout
    ).cte()
    hates_query = get_standing_query(
        session, "hate", "hates_affect_random", proofoflife_timeout
    ).cte()

    score = score_expression(
        last_played,
        never_played,
        randomness,
    ) + (func.ifnull(loves_query.c.count, 0) / num_active_users * user_rating)

    query = (
        session.query(Song.id, Song.localpath, score.label("score"))
        .select_from(Song)
        .join(ChannelStat, isouter=True)
        .join(loves_query, isouter=True)
        .join(hates_query, isouter=True)
    )
    query = query.filter(Song.duration < max_random_duration)
    query = query.filter(func.ifnull(hates_query.c.count, 0) == 0)
    query = query.order_by(text("score DESC"))  # type: ignore
    return query  # type: ignore


def _random_id_pool(session: orm.Session, size: int) -> List[int]:
    """
    Return up to *size* distinct random song ids drawn uniformly from the
    ``[MIN(id), MAX(id)]`` range (two indexed lookups; effectively free). The
    caller scores only these ids instead of the whole table. Id gaps and later
    filters trim the set slightly, which is fine.
    """
    min_id, max_id = session.query(func.min(Song.id), func.max(Song.id)).one()
    if min_id is None or max_id is None:
        return []
    if min_id >= max_id:
        return [int(min_id)]
    return list({random.randint(min_id, max_id) for _ in range(size)})


def _finalize(session: orm.Session, candidate: Any) -> Optional[Song]:
    """
    Turn a scored candidate row into a Song (closing the session), mirroring the
    original find_song tail. Returns None when there is no usable candidate.
    """
    if candidate is None:
        return None
    try:
        if not candidate.score:
            # no users are online!
            session.close()
            return None
        out = (candidate.id, candidate.localpath, float(candidate.score))
        LOG.info("Selected song (%d, %s) via smartget. Score was %4.3f", *out)
        selected_song = session.query(Song).filter(Song.id == out[0]).first()
        session.close()
        return selected_song
    except IndexError:
        LOG.warning(
            "No song returned from query. Is the database empty?", exc_info=True
        )
        session.close()
        return None


def find_song(
    session: orm.Session,
    scoring_config: Mapping[ScoringConfig, int],
    is_mysql: bool,
    channel_name: Optional[str] = None,
) -> Optional[Song]:
    # pylint: disable=too-many-statements, too-many-locals
    #
    # This may be difficult to refactorl The high count of statements and
    # locals comes partly from constructing the select-query and fetching
    # settings. Ignoring this warning for now.
    """
    determine a song that would be best to play next and return it
    """

    # setup song scoring coefficients
    user_rating = scoring_config[ScoringConfig.USER_RATING]
    last_played = scoring_config[ScoringConfig.LAST_PLAYED]
    never_played = scoring_config[ScoringConfig.NEVER_PLAYED]
    randomness = scoring_config[ScoringConfig.RANDOMNESS]
    max_random_duration = scoring_config[ScoringConfig.MAX_DURATION]
    proofoflife_timeout = scoring_config[ScoringConfig.PROOF_OF_LIFE_TIMEOUT]

    if is_mysql:
        num_active_users = (
            session.query(User.id)
            .filter(
                func.unix_timestamp(User.proof_of_listening)
                + proofoflife_timeout
                > func.unix_timestamp(func.now())
            )
            .count()
        )
        if num_active_users == 0:
            # no users online
            query = smart_random_no_users(
                session,
                never_played,
                last_played,
                randomness,
                max_random_duration,
            )
        else:
            query = smart_random_with_users(
                session,
                never_played,
                user_rating,
                last_played,
                proofoflife_timeout,
                randomness,
                max_random_duration,
                num_active_users,
            )
    else:
        raise Exception(
            "SQLite support discontinued since revision 346. It may reappear in the future!"
        )

    query = query.filter(not_(Song.broken))  # type: ignore
    query = query.filter(not_(Song.exclude_from_random))  # type: ignore
    dp_channel = (
        Channel.by_name(session, channel_name) if channel_name else None
    )
    query = DynamicPlaylist.apply_to(  # type: ignore
        query, dp_channel.id if dp_channel else None
    )
    unfiltered_query = query
    mood_range = (
        Channel.mood_range(session, channel_name) if channel_name else None
    )

    # Candidate-pool fast-path: when no mood window bounds the scan and pooling
    # is enabled, score only a bounded random id-pool instead of the whole
    # table (O(pool) instead of O(N)). If the pool yields a song, use it;
    # otherwise fall through to the unchanged full-table behaviour so a pick is
    # never silent. When a mood window IS active it already bounds the scan via
    # the mood index, so that path is left untouched.
    pool_size = scoring_config.get(ScoringConfig.CANDIDATE_POOL_SIZE, 0)
    if pool_size > 0 and mood_range is None:
        pool = _random_id_pool(session, pool_size)
        if pool:
            pooled_candidate = (
                unfiltered_query.filter(Song.id.in_(pool))  # type: ignore
                .limit(10)
                .offset(0)
                .first()
            )
            if pooled_candidate is not None:
                return _finalize(session, pooled_candidate)

    if mood_range is not None:
        low, high = mood_range
        query = query.filter(
            or_(
                Song.mood_score.is_(None),
                Song.mood_score.between(low, high),
            )
        )
    query = query.limit(10)  # type: ignore
    query = query.offset(0)  # type: ignore
    candidate = query.first()

    if candidate is None and mood_range is not None:
        LOG.info(
            "No candidates inside mood range %r; falling back to an "
            "unfiltered pick",
            mood_range,
        )
        candidate = unfiltered_query.limit(10).offset(0).first()

    return _finalize(session, candidate)
