import logging
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Query
from sqlalchemy.sql import and_, func, or_, select
from wickedjukebox.demon.dbmodel import (Session, Song, albumTable,
                                         artistTable, channelSongs,
                                         dynamicPLTable, settingTable,
                                         songStandingTable, songTable,
                                         usersTable, Channel)
from wickedjukebox.demon.plparser import ParserSyntaxError, parse_query
from wickedjukebox.config import Config, ConfigKeys

from .interface import PlayMode, RandomItem

LOG = logging.getLogger(__name__)


class RandomWR2(PlayMode):

    def __init__(self, session: Session, channel_id: int) -> None:
        self.session = session
        self.channel_id = channel_id

    def bootstrap(self) -> None:
        pass

    def fetch_candidates(self) -> List[RandomItem]:
        query = self.session.query(Channel).filter_by(id=self.channel_id)
        channel = query.one()
        try:
            # get settings
            user_rating = Config.get(
                ConfigKeys.SCORING_USERRATING,
                4,
                channel=channel.name,
                converter=int
            )
            never_played = Config.get(
                ConfigKeys.SCORING_NEVERPLAYED,
                4,
                channel=channel.name,
                converter=int
            )

            # fetch the channel ssettings for online users
            user_settings = self._get_user_settings()
            online_users = list(user_settings.keys())

            # first, we fetch a limited number of songs using the basic stats.
            # This will prevent too many queries when determining love/hate stats.
            rough_query = self._get_rough_query()

            results = []
            count_added = 0
            users_affecting_hate = [x for x in user_settings
                                    if int(user_settings[x].setdefault(
                                        "hates_affect_random", 0)) == 1]
            users_affecting_love = [x for x in user_settings
                                    if int(user_settings[x].setdefault(
                                        "loves_affect_random", 0)) == 1]
            LOG.debug("Haters: %r", users_affecting_hate)
            LOG.debug("Happy People: %r", users_affecting_love)
            for row in self.session.execute(rough_query):
                # if the song is hated by someone, don't consider it further
                hate_count = self._get_standing_count(
                    row[0], users_affecting_hate, 'hate')
                if hate_count > 0:
                    continue

                # count the loves, for points calculation
                love_count = self._get_standing_count(
                        row[0], users_affecting_love, 'love')

                # okay... let's do the scoring, first, zero in:
                score = 0.0
                # now, promote loved songs
                if online_users:
                    score = score + (user_rating * (
                        float(love_count) / len(online_users)))
                # give songs that have never been played a fair chance too:
                if not row[2]:
                    score = score + never_played

                # construct a string representation of the recency of the song.
                # using the number of minutes since it's last played. If it
                # hasn't, we'll assume 1. jan. 1900.  We then zero-pad this,
                # reverse the string and prefix the score. This will give us a
                # usable sort key to sort by score descending, then by recency
                # ascending.
                delta = datetime.now() - (row[2] and row[2] or datetime(
                    1900, 1, 1))
                num_delta = "%08d" % (
                    delta.days * 24 * 60 + delta.seconds / 60)
                # num_delta = num_delta[::-1] # reverses the string
                key_score = "%05.2f" % score
                key_score = key_score.replace(".", "")
                sortkey = "%s%s" % (key_score, num_delta)
                results.append(RandomItem(
                    row[0],
                    {
                        "score": score,
                        "love_count": love_count,
                        "duration": row[1],
                        "last_played": row[2],
                        "sortkey": sortkey
                    }
                ))
                count_added += 1
                if count_added == 10:
                    break

            results = sorted(results, key=lambda x: x[1]['sortkey'])
            return results

        except Exception:  # pylint: disable=broad-except
            # catchall for graceful degradation
            LOG.exception("Unable to fetch any candidates!", exc_info=True)
            return []

    def get(self) -> Optional[Song]:
        candidates = self.fetch_candidates()
        if not candidates:
            LOG.warning("No song returned!")
            return None
        song = self.session.query(Song).filter(
            songTable.c.id == candidates[0][0]).first()
        return song

    def test(self) -> List[RandomItem]:
        candidates = self.fetch_candidates(self.channel_id)
        return candidates[0:10]

    def apply_dynamic_playlist(self, query):
        """
        Apply a "WHERE" clause to *query* to honour "dynamic playlists"
        """
        # keep only songs that satisfy the dynamic playlist query for this channel
        sel = select([dynamicPLTable.c.query, dynamicPLTable.c.probability])
        sel = sel.where(dynamicPLTable.c.group_id > 0)
        sel = sel.where(dynamicPLTable.c.channel_id == self.channel_id)

        # only one query will be parsed. for now.... this is a big TODO
        # as it triggers an unexpected behaviour (bug). i.e.: Why the
        # heck does it only activate one playlist?!?
        dpl = self.session.execute(sel).fetchone()
        if dpl:
            try:
                rnd = random.random()
                LOG.debug("Random value=%3.2f, playlist probability=%3.2f",
                          rnd, dpl["probability"])
                if dpl and rnd <= dpl["probability"] and parse_query(dpl["query"]):
                    query = query.where(
                        "(%s)" % parse_query(dpl["query"]))
            except ParserSyntaxError:
                LOG.error('Query was: %s', dpl.query, exc_info=True)
            except Exception:  # pylint: disable=broad-except
                # catchall for graceful degradation
                LOG.exception('Unhandled Exception')
        return query

    def _get_rough_query(self) -> Query:
        """
        Construct a first selection of songs. This is later expanded to
        calculate a more exact scoring
        """
        query = self.session.query(Channel).filter_by(id=self.channel_id)
        channel = query.one()
        recency_threshold = Config.get(
            ConfigKeys.RECENCY_THRESHOLD,
            120,
            channel=channel.name,
            converter=int,
        )
        max_random_duration = Config.get(
            ConfigKeys.MAX_RANDOM_DURATION,
            600,
            channel=channel.name,
            converter=int
        )
        rough_query = select(
            [
                songTable.c.id,
                songTable.c.duration,
                channelSongs.c.lastPlayed
            ],
            from_obj=[
                songTable.outerjoin(
                    channelSongs,
                    songTable.c.id == channelSongs.c.song_id
                ).outerjoin(
                    albumTable,
                    songTable.c.album_id == albumTable.c.id
                ).outerjoin(
                    artistTable,
                    songTable.c.artist_id == artistTable.c.id
                )
            ]
        )

        # skip songs that are too long
        rough_query = rough_query.where(
            songTable.c.duration < max_random_duration)

        # skip songs that have been recently played
        delta = timedelta(minutes=recency_threshold)
        old_time = datetime.now() - delta
        rough_query = rough_query.where(or_(
            channelSongs.c.lastPlayed < old_time,
            channelSongs.c.lastPlayed == None))  # pylint: disable=singleton-comparison

        # skip unavailable songs
        rough_query = rough_query.where(songTable.c.available == 1)

        rough_query = self.apply_dynamic_playlist(rough_query)

        # bring in some random
        rough_query = rough_query.order_by(func.rand())

        # now keep only a selected few
        rough_query = rough_query.limit(200)
        return rough_query

    def _get_user_settings(self) -> Dict[int, Dict[str, Any]]:
        """
        Fetch the settings of all listening users as a dict of dicts. First
        key is the user_id. The dict contained therein are the settings.

        @return: A dict of dicts
        """
        proofoflife_timeout = Config.get(
            ConfigKeys.PROOFOFLIFE_TIMEOUT,
            120,
            converter=int
        )
        listeners_query = select(
            [
                usersTable.c.id,
                usersTable.c.username,
                settingTable.c.var,
                settingTable.c.value,
            ],
            from_obj=[
                usersTable.join(
                    settingTable,
                    and_(
                        usersTable.c.id == settingTable.c.user_id,
                        settingTable.c.channel_id == self.channel_id
                    )
                )
            ]
        )
        listeners_query = listeners_query.where(
            func.unix_timestamp(usersTable.c.proof_of_listening) +
            proofoflife_timeout > func.unix_timestamp(func.now()))
        result = self.session.execute(listeners_query)
        online_users = set()
        user_settings = {}  # type: Dict[int, Dict[str, Any]]
        for row in result:
            online_users.add(row[0])
            user_settings.setdefault(row[0], {})
            user_settings[row[0]][row[2]] = row[3]

        LOG.debug("The following users are online: %r", online_users)
        LOG.debug("User settings:")
        LOG.debug(user_settings)
        return user_settings

    def _get_standing_count(self,
                            song_id: int,
                            user_list,
                            standing) -> int:
        if not user_list:
            return 0

        query = self.session.query(songStandingTable.c.user_id)
        query = query.filter_by(standing = standing)
        query = query.filter_by(song_id = song_id)
        query = query.filter(songStandingTable.c.user_id.in_(user_list))
        hate_count = query.count()
        return hate_count
