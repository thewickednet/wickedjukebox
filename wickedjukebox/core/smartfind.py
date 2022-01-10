"""
This module contains an entry point to run a "smart" query to find the next best
song taking channel statistics into account.
"""
import logging
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping, Optional

import sqlalchemy.orm as orm
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import func
from sqlalchemy.sql.elements import not_
from sqlalchemy.sql.expression import and_, text

from wickedjukebox.model.db.auth import User
from wickedjukebox.model.db.library import Song, UserSongStanding
from wickedjukebox.model.db.settings import Setting
from wickedjukebox.model.db.stats import ChannelStat
from wickedjukebox.smartplaylist.dbbridge import parse_dynamic_playlists

if TYPE_CHECKING:
    from typing import Tuple

LOG = logging.getLogger(__name__)

#: A song gains the maximum "last-played" score boost after this many seconds
LAST_PLAYED_CUTOFF = 7 * 24 * 60 * 60

#: A song gains a boost related to its age in the DB. This value defines a
#: relative point in time when it received the maximum value. TODO: Whether this
#: is based on recency or primacy needs to be digested from the source-code and
#: clarified.
SONG_AGE_CUTOFF = 14 * 24 * 60 * 60


class ScoringConfig(Enum):
    """
    Possible configuration values to influence the scoring query
    """

    USER_RATING = "user_rating"
    LAST_PLAYED = "last_played"
    SONG_AGE = "song_age"
    NEVER_PLAYED = "never_played"
    RANDOMNESS = "randomness"
    MAX_DURATION = "max_duration"
    PROOF_OF_LIFE_TIMEOUT = "proof_of_life"


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


def score_expression(
    last_played: int, never_played: int, song_age: int, randomness: float
):
    """
    Generates a column-expression that calculates the scoring for a song without
    taking into account user-statistics.
    """
    return (
        0
        - func.ifnull(
            ChannelStat.last_played_parametric(LAST_PLAYED_CUTOFF, last_played),
            LAST_PLAYED_CUTOFF,
        )
        + func.if_(ChannelStat.lastPlayed is None, never_played, 0)
        + func.ifnull(
            func.if_(
                (func.now() - Song.added) < SONG_AGE_CUTOFF,
                (func.now() - Song.added) / SONG_AGE_CUTOFF * song_age,
                0,
            ),
            0,
        )
        + ((func.rand() * randomness * 2) - randomness)
    )


def smart_random_no_users(
    session,
    never_played: int,
    last_played: int,
    song_age: int,
    randomness: float,
    max_random_duration: int,
):
    """
    Fetch a random song without taking any user-statistics into account. Only
    consider channel statistics.

    :param never_played: A score bonus for songs that have never been played.
    :param last_played: The maximum score boost for songs that have not been
        played in a while.
    :param song_age: The maximum score boost for songs related to the date they
        were added to the database. NOTE: I don't remember if they get mex score
        if they are *recent* or if they are *old*. Needs to be clarified.
    :randomness: A score modifier adding a dash of randomness to the overall
        score.
    :max_random_duration: Don't return songs with a longer duration than this
        value (in seconds).
    """

    query = (
        session.query(
            Song.id,
            Song.localpath,
            score_expression(
                last_played, never_played, song_age, randomness
            ).label("score"),
        )
        .select_from(Song)
        .join(ChannelStat, isouter=True)
    )
    query = query.filter(Song.duration < max_random_duration)
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
    song_age: int,
    max_random_duration: int,
    num_active_users: int,
) -> "Query[Tuple[int, str, float]]":

    """
    song.id
    song.localpath
    score =
        - seconds since last played (capped of at lp_cutoff) divided by lp_cutoff multiplied by "last-played" scoring weight
    """

    loves_query = get_standing_query(
        session, "love", "loves_affect_random", proofoflife_timeout
    ).cte()
    hates_query = get_standing_query(
        session, "hate", "hates_affect_random", proofoflife_timeout
    ).cte()

    score = (
        score_expression(
            last_played,
            never_played,
            song_age,
            randomness,
        )
        + (func.ifnull(loves_query.c.count, 0) / num_active_users * user_rating)
    )

    query = (
        session.query(Song.id, Song.localpath, score.label("score"))
        .select_from(Song)
        .join(ChannelStat, isouter=True)
        .join(loves_query, isouter=True)
        .join(hates_query, isouter=True)
    )
    query = query.filter(Song.duration < max_random_duration)
    query = query.filter(func.ifnull(hates_query.c.count, 0) == 0)
    query = query.filter(Song.duration < max_random_duration)
    query = query.order_by(text("score DESC"))  # type: ignore
    return query  # type: ignore


def find_song(
    session: orm.Session,
    scoring_config: Mapping[ScoringConfig, int],
    is_mysql: bool,
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
    song_age = scoring_config[ScoringConfig.SONG_AGE]
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
                song_age,
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
                song_age,
                max_random_duration,
                num_active_users,
            )
    else:
        raise Exception(
            "SQLite support discontinued since revision 346. It may reappear in the future!"
        )

    query = query.filter(not_(Song.broken))  # type: ignore

    # TODO: Add dynamic playlist clauses
    query = query.where(and_(True, *parse_dynamic_playlists()))

    query = query.limit(10)  # type: ignore
    query = query.offset(0)  # type: ignore
    candidate = query.first()

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
