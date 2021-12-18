"""
This module contains some of the more complex SQL queries to keep the rest of
the code a bit more readable
"""
# pylint: disable=no-member


from typing import Any, TYPE_CHECKING
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import text, alias, join, func, and_
from wickedjukebox.demon.dbmodel import (
    Song,
    channelSongs,
    Artist,
    Album,
    settingTable,
    songStandingTable,
    usersTable,
)

if TYPE_CHECKING:
    from typing import Tuple


#: A song gains the maximum "last-played" score boost after this many seconds
LAST_PLAYED_CUTOFF = 7 * 24 * 60 * 60

#: A song gains a boost related to its age in the DB. This value defines a
#: relative point in time when it received the maximum value. TODO: Whether this
#: is based on recency or primacy needs to be digested from the source-code and
#: clarified.
SONG_AGE_CUTOFF = 14 * 24 * 60 * 60


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
                join(songStandingTable, usersTable),
                settingTable,
                onclause=and_(
                    settingTable.c.var == setting_name,  # type: ignore
                    usersTable.c.id == settingTable.c.user_id,  # type: ignore
                ),
                isouter=True,
            )
        )
        .where(
            songStandingTable.c.standing == standing,
            func.ifnull(settingTable.c.value, 1) == 1,  # type: ignore
            func.unix_timestamp(usersTable.c.proof_of_listening)
            + proofoflife_timeout
            > func.unix_timestamp(func.now()),
        )
        .group_by(songStandingTable.c.song_id)
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
                    alias(channelSongs, "c"),
                    isouter=True,
                    onclause=text("c.song_id = s.id")
                ),
                alias(Artist, "a"),  # type: ignore
                onclause=text("s.artist_id = s.artist_id")
            ),
            alias(Album, "b"),  # type: ignore
            onclause=text("s.album_id = b.id")
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
                            channelSongs,
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
