"""
This module contains an entry point to run a "smart" query to find the next best
song taking channel statistics into account.
"""
import logging
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping, Optional

import sqlalchemy.orm as orm
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import func, select
from sqlalchemy.sql.elements import not_
from sqlalchemy.sql.expression import alias, and_, join, text

from wickedjukebox.config import Config, ConfigKeys
from wickedjukebox.model.db import (
    Album,
    Artist,
    ChannelStat,
    Setting,
    Song,
    User,
    UserSongStanding,
)
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
    standing: str, setting_name: str, proofoflife_timeout: int
) -> "Query[Any]":
    """
    Return a query retrieving the number of users that either "hate" or "love" a
    given song. Only users that have been listening within the last
    *proofoflife_timeout* seconds will be taken into account.
    """
    query: Query[Any] = (
        select([Song.id, func.count().label("standing")])  # type: ignore
        .select_from(
            join(
                join(UserSongStanding, User),
                Setting,
                onclause=and_(
                    Setting.var == setting_name,  # type: ignore
                    User.id == Setting.user_id,  # type: ignore
                ),
                isouter=True,
            )
        )
        .where(
            UserSongStanding.standing == standing,
            func.ifnull(Setting.value, 1) == 1,  # type: ignore
            func.unix_timestamp(User.proof_of_listening) + proofoflife_timeout
            > func.unix_timestamp(func.now()),
        )
        .group_by(UserSongStanding.song_id)
    )
    return query


def smart_random_no_users(
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

    select_object = text(
        """
        s.id,
        s.localpath,
        (
            (
                IFNULL(least(:lp_cutoff, (NOW()-lastPlayed)), :lp_cutoff)
                - :lp_cutoff
            ) / :lp_cutoff * :last_played
        )
        + IF(lastPlayed IS NULL, :never_played, 0)
        + IFNULL(
            IF(
                (NOW()-s.added)<:sa_cutoff,
                (NOW()-s.added)/:sa_cutoff * :song_age,
                0
            ),
            0
            )
        + ((RAND()*:randomness*2)-:randomness)
        AS score
        """
    ).bindparams(
        never_played=never_played,
        last_played=last_played,
        randomness=randomness,
        song_age=song_age,
        lp_cutoff=LAST_PLAYED_CUTOFF,
        sa_cutoff=SONG_AGE_CUTOFF,
    )
    query = select(select_object)  # type: ignore
    query = query.select_from(
        join(
            join(
                join(
                    alias(Song, "s"),  # type: ignore
                    alias(ChannelStat, "c"),
                    isouter=True,
                    onclause=text("c.song_id = s.id"),
                ),
                alias(Artist, "a"),  # type: ignore
                onclause=text("s.artist_id = s.artist_id"),
            ),
            alias(Album, "b"),  # type: ignore
            onclause=text("s.album_id = b.id"),
        )
    )

    query = query.where(text("s.duration < :max_duration").bindparams(max_duration=max_random_duration))  # type: ignore
    query = query.order_by(text("score DESC"))
    query = query.limit(10)
    query = query.offset(0)

    return query


def smart_random_with_users(
    never_played: int,
    user_rating: int,
    last_played: int,
    proofoflife_timeout: int,
    randomness: float,
    song_age: int,
    max_random_duration: int,
) -> "Query[Tuple[int, str, float]]":
    select_object = text(
        """
        s.id,
        s.localpath,
        (
            (
                IFNULL(least(:lp_cutoff, (NOW()-lastPlayed)), :lp_cutoff)
                - :lp_cutoff
            ) / :lp_cutoff * :last_played
        )
        + (
            (
                IFNULL(ls.standing, 0)
            )
            / (
                SELECT COUNT(*) FROM users
                WHERE UNIX_TIMESTAMP(proof_of_listening) + :proof_of_life > UNIX_TIMESTAMP(NOW())
              ) * :user_rating
          )
        + IF(lastPlayed IS NULL, :never_played, 0)
        + IFNULL(
            IF(
                (NOW()-s.added)<:sa_cutoff,
                (NOW()-s.added)/:sa_cutoff * :song_age,
                0
            ),
            0
            )
        + ((RAND()*:randomness*2)-:randomness)
        AS score
        """
    ).bindparams(
        never_played=never_played,
        last_played=last_played,
        randomness=randomness,
        song_age=song_age,
        user_rating=user_rating,
        proof_of_life=proofoflife_timeout,
        lp_cutoff=LAST_PLAYED_CUTOFF,
        sa_cutoff=SONG_AGE_CUTOFF,
    )
    query = select(select_object)  # type: ignore
    loves_query = get_standing_query(
        "love", "loves_affect_random", proofoflife_timeout
    )
    hates_query = get_standing_query(
        "hate", "hates_affect_random", proofoflife_timeout
    )
    query = query.select_from(
        join(
            join(
                join(
                    join(
                        join(
                            alias(Song, "s"),  # type: ignore
                            ChannelStat,
                            isouter=True,
                        ),
                        alias(loves_query.subquery(), "ls"),  # type: ignore
                        isouter=True,
                    ),
                    alias(hates_query.subquery(), "hs"),  # type: ignore
                    isouter=True,
                ),
                Artist,  # type: ignore
            ),
            Album,  # type: ignore
        ),
    )
    query = query.where(  # type: ignore
        Song.duration < max_random_duration,  # type: ignore
        func.ifnull(text("hs.standing"), 0) == 0,  # type: ignore
    )
    query = query.order_by(text("score DESC"))  # type: ignore
    query = query.limit(10)  # type: ignore
    query = query.offset(0)  # type: ignore
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

        query = session.query(User.id).filter(
            func.unix_timestamp(User.proof_of_listening) + proofoflife_timeout
            > func.unix_timestamp(func.now())
        )
        if query.count() == 0:
            # no users online
            query = smart_random_no_users(
                never_played,
                last_played,
                song_age,
                randomness,
                max_random_duration,
            )
        else:
            query = smart_random_with_users(
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
            "SQLite support discontinued since revision 346. It may reappear in the future!"
        )

    query = query.where(not_(text("s.broken")))  # type: ignore

    # TODO: Add dynamic playlist clauses
    # TODO fix cross-product issue query = query.where(and_(*parse_dynamic_playlists()))
    query = query.where(and_(*parse_dynamic_playlists()))

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
