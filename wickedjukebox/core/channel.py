# pylint: disable=missing-docstring, invalid-name, import-error, useless-object-inheritance
# TODO: Set progress
#    State.set("progress", 0, __CHANNEL_ID)

import logging
import os
import time
from datetime import datetime
from random import choice, random

from pusher import Pusher
from sqlalchemy.sql import func, or_, select, update
from wickedjukebox.config import (
    Config,
    ConfigKeys,
    load_config,
    parse_param_string,
)
from wickedjukebox.demon.dbmodel import Album, Artist
from wickedjukebox.demon.dbmodel import Channel as DbChannel
from wickedjukebox.demon.dbmodel import (ChannelStat, Session, Song,
                                         State, channelSongs, channelTable,
                                         songTable, usersTable)
from wickedjukebox.demon.players import common

LOG = logging.getLogger(__name__)
DEFAULT_RANDOM_MODE = 'random_wr2'
DEFAULT_QUEUE_MODE = 'queue_positioned'
MAX_INTERNAL_PLAYLIST_SIZE = 3


class JingleArtist(object):  # pylint: disable=too-few-public-methods
    name = '<none>'


class Jingle(object):  # pylint: disable=too-few-public-methods

    def __init__(self, id_, localpath):
        # type: (int, str) -> None
        self.id = id_
        self.localpath = localpath
        self.title = 'jingle'
        self.artist = JingleArtist()

    def __repr__(self):
        # type: () -> str
        return '<Jingle %r %r>' % (self.id, self.localpath)


class Channel(object):

    def __init__(self, session, name, pusher_client=None):
        # type: (Session, str, Pusher) -> None

        self.__scrobbler = None
        self.__keepRunning = True
        self.__playStatus = 'stopped'
        self.__randomstrategy = None
        self.__queuestrategy = None
        self.__no_jingle_count = 0
        self.__config = load_config()
        self.__session = session
        self.id = None
        self.name = None
        self.last_tagged_song = None

        query = session.query(DbChannel).filter(DbChannel.name == name)
        channel_data = query.one_or_none()
        if not channel_data:
            raise ValueError("Failed to load channel %s from database. "
                             "Please make sure that the named channel exists "
                             "in the database table called 'channel'" % name)

        self.name = channel_data.name
        LOG.debug("Loaded channel %s", self.name)

        player_params = parse_param_string(channel_data.backend_params)
        self.__player = common.make_player(channel_data.backend,
                                           channel_data.id,
                                           player_params)
        self.__player.connect()

        self.id = channel_data.id

        if pusher_client:
            self.__pusher_client = pusher_client
        else:
            self.__pusher_client = Pusher(
                app_id=self.__config.get('pusher', 'app_id'),
                key=self.__config.get('pusher', 'key'),
                secret=self.__config.get('pusher', 'secret'),
                cluster=self.__config.get('pusher', 'cluster'),
                ssl=True
            )

        LOG.info("Initialised channel %s with ID %d", self.name, self.id)

    def emit_internal_playlist(self):
        # type: () -> None
        LOG.info('emitting internal queue to pusher')
        payload = [song._asdict() for song in self.__player.upcoming_songs()]
        try:
            self.__pusher_client.trigger('wicked', 'internal_queue', payload)
        except Exception:  # pylint: disable=broad-except
            # catchall for graceful degradation
            LOG.warning('Unandled exception in pusher submission',
                        exc_info=True)

    def isStopped(self):
        # type: () -> bool
        return self.__playStatus == 'stopped'

    def close(self):
        # type: () -> None
        LOG.debug("Closing channel...")
        self.stopPlayback()

        if self.__scrobbler is not None:
            self.__scrobbler.stop()
            self.__scrobbler.join()

        if self.__keepRunning:
            self.__keepRunning = False

    def setBackend(self, backend):
        raise NotImplementedError

    def queueSong(self, song):
        # type: (Song) -> bool

        LOG.info("Queueing %r", song)

        session = self.__session

        # re-attach the song instance to the new session
        if isinstance(song, Song):
            song = session.merge(song)

        # queue the song
        was_successful = self.__player.queue({
            'filename': song.localpath,
            'artist': song.artist.name,
            'title': song.title})

        if isinstance(song, Song) and self.__scrobbler is not None:
            a = session.query(Artist).get(song.artist_id)
            b = session.query(Album).get(song.album_id)
            if a and b:
                try:
                    self.__scrobbler.now_playing(
                        artist=a.name,
                        track=song.title,
                        album=b.name,
                        length=int(song.duration),
                        trackno=int(song.track_no))
                except TypeError as ex:
                    LOG.error(ex, exc_info=True)
        session.close()
        return was_successful

    def queue_songs(self):
        # type: () -> None
        if self.__player.playlistSize() > MAX_INTERNAL_PLAYLIST_SIZE:
            LOG.debug('Internal playlist size exceeds maximal length. '
                      'Not appending songs!')
            self.__player.crop_playlist(MAX_INTERNAL_PLAYLIST_SIZE)
            return
        while True:
            next_songs = self.getNextSongs()
            successes = []
            for song in next_songs:
                successes.append(self.queueSong(song))
            if any(successes):
                break
            LOG.warning('Something went wrong appending songs. Retrying...')
        self.emit_internal_playlist()

    def startPlayback(self):
        # type: () -> str
        self.__playStatus = 'playing'
        self.queue_songs()
        self.__player.start()
        return 'OK'

    def pausePlayback(self):
        # type: () -> str
        self.__playStatus = 'paused'
        self.__player.pause()
        return 'OK'

    def stopPlayback(self):
        # type: () -> str
        self.__playStatus = 'stopped'
        self.__player.stop()
        return 'OK'

    def skipSong(self, current_song_entity):
        # type: (Song) -> str
        """
        Updates play statistics and sends a "next" command to the player
        backend
        """

        if current_song_entity is None:
            return ''

        LOG.info("skipping song")

        session = Session()
        query = session.query(ChannelStat)
        query = query.filter(songTable.c.id == channelSongs.c.song_id)
        query = query.filter(songTable.c.id == current_song_entity.id)
        query = query.filter(channelSongs.c.channel_id == self.id)
        stat = query.first()
        if not stat:
            stat = ChannelStat(song_id=current_song_entity.id,
                               channel_id=self.id)
            stat.skipped = 1
            stat.lastPlayed = datetime.now()
            session.add(stat)
        else:
            stat.skipped = stat.skipped + 1
            stat.lastPlayed = datetime.now()
        session.commit()
        session.close()
        self.queue_songs()
        self.__player.skip()
        return 'OK'

    def get_jingle(self):
        # type: () -> Optional[Song]
        jingles_folder = Config.get(
            ConfigKeys.JINGLES_FOLDER,
            "",
            channel=self.name,
        ).strip()
        if not jingles_folder:
            LOG.info('No jingles folder set in the DB. No jingle will be '
                     'played')
            return None

        interval_raw = Config.get(
            ConfigKeys.JINGLES_INTERVAL,
            fallback="0",
            channel=self.name,
        )

        # This should clean up any whitespace and ensure the value is properly
        # initialised if the DB contained an all-whitespace string.
        interval = interval_raw.strip() or '0'

        # We allow setting boundaries using <min>-<max> to allow a bit of
        # random. The jingles will be played after at least <min> songs and
        # before at most <max> songs.
        if '-' in interval:
            min_, _, max_ = interval.partition('-')
            min_ = int(min_.strip())
            max_ = int(max_.strip())
            jingle_boundary = (min_, max_)
        else:
            # If there was no "-" in the value, we will play jingles after
            # exactly that many songs (<min> === <max>)
            jingle_boundary = (int(interval), int(interval))

        if 0 in jingle_boundary:
            LOG.warning('The jingle interval contained a "0" value. This '
                        'would cause the jukebox to play only jingles and is '
                        'not allowed. Review the setting value (%r)',
                        interval_raw)
            return None

        random_range = (jingle_boundary[1] - jingle_boundary[0])
        rnd = (int(random() * random_range) + self.__no_jingle_count)
        LOG.debug('Current rnadom jingle value: %r | Boundary: %r',
                  rnd, jingle_boundary)
        if jingle_boundary[0] <= rnd:
            try:
                available_jingles = os.listdir(jingles_folder)
            except OSError as ex:
                LOG.warning("Unable to open jingles: %s",
                            str(ex), exc_info=True)
                available_jingles = []
            if available_jingles:
                random_file = choice(available_jingles)
                self.__no_jingle_count = 0
                return Jingle(
                    None,
                    os.path.join(jingles_folder, random_file)
                )
        else:
            self.__no_jingle_count += 1
            LOG.debug("'No jingle' count increased to %d",
                      self.__no_jingle_count)
        return None

    def update_current_listeners(self):
        # type: () -> None
        """
        Scrape the Icecast admin page for current listeners and update theit
        state in the DB
        """
        listeners = self.__player.listeners()
        LOG.log(listeners and logging.INFO or logging.DEBUG,
                'Updating current listeners: %r', listeners)
        if listeners is None:
            # feature not supported by backend player, or list of listeners
            # unknown
            return

        for l in listeners:
            query = usersTable.update(
                or_(
                    usersTable.c.IP == l,
                    usersTable.c.pinnedIp == l
                ),
                values={usersTable.c.proof_of_listening: func.now()})
            query.execute()

    def process_upcoming_song(self):
        # type: () -> None
        session = Session()
        songs = list(self.__player.upcoming_songs())
        upcoming_id = None
        if not songs:
            LOG.debug('No upcoming song in internal queue')
        else:
            path = songs[0].filename
            # The following "LIKE" operator is used to hack around a small MPD
            # detail: Song paths are always relative to its library path, but
            # our DB contains the absolute path.
            song_entity = session.query(Song).filter(
                Song.localpath.like('%%%s' % path)
            ).first()
            if not song_entity:
                LOG.debug('Upcoming song not found in DB')
            else:
                LOG.debug('Upcoming song found with ID %d', song_entity.id)
                upcoming_id = song_entity.id

        State.set("upcoming_song", upcoming_id, self.id)
        session.commit()
        Session.close()

    def handle_song_change(self, session, last_known_song,
                           current_song_entity):
        # type: (Session, str, Song) -> bool
        if current_song_entity is None:
            return True

        if last_known_song == current_song_entity.localpath:
            return False

        LOG.debug('Current song changed from %s to %s!',
                  last_known_song, current_song_entity.localpath)

        song_id = current_song_entity.id if current_song_entity else 0
        State.set("current_song", song_id, self.id)

        try:
            self.__pusher_client.trigger('wicked', 'current', {
                'action': 'update'})
        except Exception:  # pylint: disable=broad-except
            # catchall for graceful degradation
            LOG.warning('Unandled exception in pusher submission',
                        exc_info=True)

        return True

    def run(self):
        # type: () -> None
        cycleTime = int(
            Config.get(
                ConfigKeys.CHANNEL_CYCLE,
                "3",
                channel=self.name,
            )
        )
        lastCreditGiveaway = datetime.now()
        lastPing = datetime.now()
        proofoflife_timeout = int(
            Config.get(
                ConfigKeys.PROOFOFLIFE_TIMEOUT,
                "120"
            )
        )
        current_song = self.__player.current_song()
        last_known_song = current_song

        # while we are alive, do the loop
        while self.__keepRunning:

            time.sleep(cycleTime)
            self.process_upcoming_song()
            session = Session()
            current_song = self.__player.current_song()
            current_song_entity = session.query(Song).filter(
                songTable.c.localpath == current_song
            ).first()

            # If no one is listening, pause the station. Otherwise, resume.
            if (self.__player.listeners() and
                    self.__player.status() != common.STATUS_STARTED):
                self.__player.start()
                LOG.info("Somone has come online! Resuming playback...")
            elif (not self.__player.listeners() and
                  self.__player.status() == common.STATUS_STARTED):
                self.__player.pause()
                LOG.info("No-one here... pausing playback...")

            # ping the database every 2 minutes (unless another value was
            # specified in the settings)
            if (datetime.now() - lastPing).seconds > proofoflife_timeout:
                self.update_current_listeners()
                lastPing = datetime.now()

                update(channelTable).where(
                    channelTable.c.id == self.id).values(
                        {'ping': datetime.now()}).execute()

                proofoflife_timeout = int(
                    Config.get(
                        ConfigKeys.PROOFOFLIFE_TIMEOUT,
                        "120",
                    )
                )

            skipState = State.get("skipping", self.id, default=False)
            if skipState and int(skipState) == 1:
                self.skipSong(current_song_entity)
                State.set("skipping", 0, self.id)

            # If we are not playing stuff, we can skip the rest
            if self.__playStatus != 'playing':
                continue

            # -----------------------------------------------------------------
            change_detected = self.handle_song_change(
                session, last_known_song, current_song_entity)
            if change_detected:
                last_known_song = current_song
                self.emit_internal_playlist()

            # if the song is soon finished, update stats and pick the next one
            currentPosition = self.__player.position()
            LOG.debug("Current position: %4.2f in %r",
                      currentPosition, current_song)
            State.set("progress", currentPosition, self.id)

            if current_song_entity and currentPosition > 90:
                LOG.info('Soon finished. Recording stats')
                query = session.query(ChannelStat)
                query = query.filter(
                    songTable.c.id == channelSongs.c.song_id)
                query = query.filter(
                    songTable.c.id == current_song_entity.id)
                query = query.filter(
                    channelSongs.c.channel_id == self.id)
                stat = query.first()
                if not stat:
                    stat = ChannelStat(song_id=current_song_entity.id,
                                       channel_id=self.id)
                    LOG.info("Setting last played date")
                    stat.lastPlayed = datetime.now()
                    stat.played = 1
                else:
                    LOG.info("Updating last played date")
                    stat.lastPlayed = datetime.now()
                    stat.played = stat.played + 1
                session.add(stat)
                session.commit()
                self.queue_songs()

            # if we handed out credits more than 5mins ago, we give out some
            # more
            if (datetime.now() - lastCreditGiveaway).seconds > 300:
                LOG.info('Handing out credits to users.')
                maxCredits = int(
                    Config.get(
                        ConfigKeys.MAX_CREDITS,
                        "30",
                        channel=self.name,
                    )
                )
                usersTable.update(
                    usersTable.c.credits < maxCredits,
                    values={usersTable.c.credits: usersTable.c.credits + 5}
                ).execute()
                # we may have overshot our target slightly. This fixes it
                usersTable.update(
                    usersTable.c.credits > maxCredits,
                    values={usersTable.c.credits: maxCredits}
                ).execute()
                lastCreditGiveaway = datetime.now()

            session.close()

        LOG.info("Channel stopped")
