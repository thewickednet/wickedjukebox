# TODO: Set progress
#    State.set("progress", 0, __CHANNEL_ID)

from datetime import datetime
import time
import os
from random import choice, random

from sqlalchemy.sql import select, func, update, or_

import pusher

from wickedjukebox.demon import playmodes
from wickedjukebox.demon.players import common
from wickedjukebox.demon.dbmodel import (
    channelTable,
    Setting,
    Session,
    State,
    ChannelStat,
    Artist,
    Album,
    Song,
    usersTable,
    songTable,
    queueTable,
    channelSongs)
from wickedjukebox.util import fsencode

import logging
LOG = logging.getLogger(__name__)
DEFAULT_RANDOM_MODE = 'random_wr2'
DEFAULT_QUEUE_MODE = 'queue_positioned'


class JingleArtist(object):
    name = '<none>'


class Jingle(object):

    def __init__(self, id, localpath):
        self.id = id
        self.localpath = localpath
        self.title = 'jingle'
        self.artist = JingleArtist()

    def __repr__(self):
        return '<Jingle %r %r>' % (self.id, self.localpath)


class Channel(object):

    def __init__(self, name):

        self.id = None
        self.name = None
        self.__scrobbler = None
        self.__keepRunning = True
        self.__playStatus = 'stopped'
        self.__currentSong = None
        self.__currentSongRecorded = False
        self.__currentSongFile = ''
        self.__randomstrategy = None
        self.__queuestrategy = None
        self.__jingles_folder = None
        self.__jingles_interval = 0
        self.__no_jingle_count = 0
        self.__lastfm_api = None
        self.last_tagged_song = None

        lastfm_api_key = Setting.get("lastfm_api_key", None)
        if lastfm_api_key:
            from wickedjukebox import lastfm
            self.__lastfm_api = lastfm.Api(lastfm_api_key)

        s = select([
            channelTable.c.id,
            channelTable.c.name,
            channelTable.c.backend,
            channelTable.c.backend_params,
            ])
        s = s.where(channelTable.c.name == name.decode("utf-8"))
        r = s.execute()
        self.__channel_data = r.fetchone()
        if not self.__channel_data:
            raise ValueError("Failed to load channel %s from database. "
                             "Please make sure that the named channel exists "
                             "in the database table called 'channel'" % name)

        self.name = self.__channel_data["name"]
        LOG.debug("Loaded channel %s" % self.name)

        player_params = {}
        if self.__channel_data['backend_params']:
            for param in self.__channel_data['backend_params'].split(','):
                key, value = param.split('=')
                player_params[key.strip()] = value.strip()

        self.__player = common.make_player(self.__channel_data['backend'],
                                           self.__channel_data['id'],
                                           player_params)
        self.__player.connect()

        self.id = self.__channel_data["id"]
        LOG.info("Initialised channel %s with ID %d" % (
            self.name,
            self.id))

    def isStopped(self):
        return self.__playStatus == 'stopped'

    def close(self):
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

        LOG.info("Queueing %r" % song)

        session = Session()

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
                    self.__scrobbler.now_playing(artist=a.name,
                        track=song.title,
                        album=b.name,
                        length=int(song.duration),
                        trackno=int(song.track_no))
                except TypeError, ex:
                    import traceback
                    traceback.print_exc()
                    LOG.error(ex)
        session.close()
        return was_successful

    def startPlayback(self):
        self.__playStatus = 'playing'
        nextSong = self.getNextSong()
        was_successful = self.queueSong(nextSong)
        while not was_successful:
            nextSong = self.getNextSong()
            was_successful = self.queueSong(nextSong)
        self.__player.start()
        return 'OK'

    def pausePlayback(self):
        self.__playStatus = 'paused'
        self.__player.pause()
        return 'OK'

    def stopPlayback(self):
        self.__playStatus = 'stopped'
        self.__player.stop()
        return 'OK'

    def enqueue(self, songID, userID=None):

        self.__queuestrategy = playmodes.create(Setting.get(
            'queue_model',
            DEFAULT_QUEUE_MODE, channel_id=self.id))
        self.__queuestrategy.enqueue(
                songID,
                userID,
                self.id)
        return 'OK: queued song <%d> for user <%d> on channel <%d>' % (
                songID, userID, self.id
                )

    def current_queue(self):
        self.__queuestrategy = playmodes.create(Setting.get(
            'queue_model',
            DEFAULT_QUEUE_MODE,
            channel_id=self.id))
        return self.__queuestrategy.list(self.id)

    def skipSong(self):
        """
        Updates play statistics and sends a "next" command to the player
        backend
        """

        if self.__currentSong is None:
            return

        session = Session()

        query = session.query(ChannelStat).select()
        query = query.filter(songTable.c.id == channelSongs.c.song_id)
        query = query.filter(songTable.c.id == self.__currentSong.id)
        query = query.filter(channelSongs.c.channel_id == self.id)
        stat = query.first()
        if not stat:
            stat = ChannelStat(songid=self.__currentSong.id,
                               channelid=self.id)
            stat.skipped = 1
            stat.lastPlayed = datetime.now()
        else:
            stat.skipped = stat.skipped + 1
            stat.lastPlayed = datetime.now()
        session.add(stat)

        nextSong = self.getNextSong()
        LOG.info("skipping song")

        session.close()

        self.enqueue(nextSong.id)
        self.__player.skip()
        return 'OK'

    def moveup(self, qid, delta):
        self.__queuestrategy = playmodes.create(Setting.get(
            'queue_model',
            DEFAULT_QUEUE_MODE,
            channel_id=self.id))
        self.__queuestrategy.moveup(self.id, qid, delta)

    def movedown(self, qid, delta):
        self.__queuestrategy = playmodes.create(Setting.get(
            'queue_model',
            DEFAULT_QUEUE_MODE,
            channel_id=self.id))
        self.__queuestrategy.movedown(self.id, qid, delta)

    def get_jingle(self):
        self.__jingles_folder = Setting.get(
                'jingles_folder',
                default=None,
                channel_id=self.id)
        self.__jingles_interval = Setting.get(
                'jingles_interval',
                default=None,
                channel_id=self.id)
        if self.__jingles_interval == '' or self.__jingles_interval is None:
            self.__jingles_interval = None
        elif self.__jingles_interval.find("-") > -1:
            jingle_boundary = [int(x) for x in
                    self.__jingles_interval.split("-")]
        else:
            jingle_boundary = [
                    int(self.__jingles_interval),
                    int(self.__jingles_interval)]

        if self.__jingles_folder == '':
            self.__jingles_folder = None

        if (self.__jingles_interval is not None and
                self.__jingles_folder is not None):

            try:
                rnd = (int(random() *
                       (jingle_boundary[1] - jingle_boundary[0])) +
                       self.__no_jingle_count)
                if jingle_boundary[0] <= rnd:
                    available_jingles = os.listdir(self.__jingles_folder)
                    if available_jingles != []:
                        random_file = choice(available_jingles)
                        self.__no_jingle_count = 0
                        return Jingle(
                            None,
                            os.path.join(self.__jingles_folder, random_file)
                        )
                else:
                    self.__no_jingle_count += 1
                    LOG.debug("'No jingle' count increased to %d" %
                            self.__no_jingle_count)
            except OSError, ex:
                import traceback
                traceback.print_exc()
                LOG.warning("Unable to open jingles: %s" % str(ex))

    def update_current_listeners(self):
        """
        Scrape the Icecast admin page for current listeners and update theit
        state in the DB
        """
        listeners = self.__player.listeners()
        LOG.log(listeners and logging.INFO or logging.DEBUG,
                'Updating current listeners: %r' % listeners)
        if listeners is None:
            # feature not supported by backedd player, or list of listeners
            # unknown
            return []

        for l in listeners:
            query = usersTable.update(
                or_(
                    usersTable.c.IP == l,
                    usersTable.c.pinnedIp == l
                ),
                values={usersTable.c.proof_of_listening: func.now()})
            query.execute()

    def process_upcoming_song(self):
        # A state "upcoming_song" with value -1 means that the upcoming song is
        # unwanted and a new one should be triggered if possible
        state = State.get("upcoming_song", self.id, default=None)
        if state and int(state) == -1:
            LOG.info("Prefetching new song as the current upcoming_song "
                    "was unwanted.")
            self.__randomstrategy.prefetch(self.id, async=False)

        if self.__randomstrategy:
            upcoming = self.__randomstrategy.peek(self.id)
            if upcoming:
                State.set("upcoming_song", upcoming.id, self.id)
            else:
                State.set("upcoming_song", None, self.id)
        else:
            State.set("upcoming_song", None, self.id)

    def getNextSong(self):
        LOG.info('Determining next song to play...')
        self.__randomstrategy = playmodes.create(Setting.get(
            'random_model',
            DEFAULT_RANDOM_MODE,
            channel_id=self.id))
        self.__queuestrategy = playmodes.create(Setting.get(
            'queue_model',
            DEFAULT_QUEUE_MODE,
            channel_id=self.id))
        self.__randomstrategy.bootstrap(self.id)

        nextSong = self.get_jingle()
        LOG.info('Jingle: %r' % nextSong)

        if not nextSong:
            nextSong = self.__queuestrategy.dequeue(self.id)
            LOG.info('Queue: %r' % nextSong)

        if not nextSong:
            nextSong = self.__randomstrategy.get(self.id)
            LOG.info('Random song: %r' % nextSong)

        # handle orphaned files
        while (not os.path.exists(fsencode(nextSong.localpath)) and
               self.__keepRunning):
            LOG.warning("%r not found!" % nextSong.localpath)
            songTable.update(songTable.c.id == nextSong.id,
                             values={'broken': True}).execute()

            nextSong = self.__randomstrategy.get(self.id)
            LOG.info('Random song: %r' % nextSong)

        return nextSong

    def run(self):
        cycleTime = int(Setting.get(
            'channel_cycle',
            default='3',
            channel_id=self.id))
        lastCreditGiveaway = datetime.now()
        lastPing = datetime.now()
        proofoflife_timeout = int(Setting.get("proofoflife_timeout", 120))

        pusher_client = pusher.Pusher(
            app_id='<app_id>',
            key='<app_key>',
            secret='<app_secret>',
            cluster='eu',
            ssl=True
        )

        # while we are alive, do the loop
        while self.__keepRunning:

            time.sleep(cycleTime)
            self.process_upcoming_song()
            session = Session()

            # If no one is listening, pause the station. Otherwise, resume.
            if (self.__player.listeners() and
                    self.__player.status() != icecast.STATUS_STARTED):
                self.__player.start()
                LOG.info("Somone has come online! Resuming playback...")
            elif (not self.__player.listeners() and
                    self.__player.status() == icecast.STATUS_STARTED):
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

                proofoflife_timeout = int(Setting.get(
                    "proofoflife_timeout",
                    120))

            # check if the player accidentally went into the "stop" state
            if (self.__player.status() == 'stopped' and
                    self.__playStatus == 'playing'):
                # This most likely means we hit the end of the playlist:
                #    - clear the playlist
                #    - add the next song to the playlist and
                #    - start playback


                nextSong = self.getNextSong()

                if not nextSong:
                    LOG.debug("What? Still nothing? Either nobody is online, "
                              "or the database is empty")
                    continue

                if isinstance(nextSong, basestring):
                    # we got a simple file. Not a tracked library song!
                    LOG.info("Queuing song %s" % nextSong)
                    was_successful = self.queueSong(nextSong)
                    while not was_successful:
                        nextSong = self.getNextSong()
                        was_successful = self.queueSong(nextSong)
                    LOG.info("Starting playback...")
                    self.__player.start()
                else:
                    was_successful = self.queueSong(nextSong)
                    while not was_successful:
                        nextSong = self.getNextSong()
                        was_successful = self.queueSong(nextSong)
                    self.__player.start()

            # or if it accidentally went into the play state
            if (self.__player.status() == 'started' and
                    self.__playStatus == 'stopped'):
                self.__player.stop()

            skipState = State.get("skipping", self.id, default=False)
            if skipState and int(skipState) == 1:
                State.set("skipping", 0, self.id)
                nextSong = self.getNextSong()
                was_successful = self.queueSong(nextSong)
                while not was_successful:
                    nextSong = self.getNextSong()
                    was_successful = self.queueSong(nextSong)
                self.__player.skip()

            # If we are not playing stuff, we can skip the rest
            if self.__playStatus != 'playing':
                continue

            # -----------------------------------------------------------------
            if self.__currentSongFile != self.__player.current_song() \
                    and self.__player.current_song() is not None:
                song = session.query(Song).filter(
                        songTable.c.localpath == self.__player.current_song()
                        ).first()

                if song:
                    self.__currentSong = song
                    # update state in database
                    State.set("current_song", song.id, self.id)
                else:
                    self.__currentSong = None
                    State.set("current_song", 0, self.id)

                pusher_client.trigger('wicked', 'current', {'action': 'update'})

                self.__currentSongRecorded = False
                self.__currentSongFile = self.__player.current_song()

            # update tags for the current song
            if (self.last_tagged_song != self.__currentSong and
                    self.__lastfm_api):
                pass  # TODO: currently disabled until it can be handled in a thread

            # if the song is soon finished, update stats and pick the next one
            currentPosition = self.__player.position()
            LOG.debug("Current position: %4.2f in %r" % (currentPosition,
                self.__player.current_song()))
            State.set("progress", currentPosition, self.id)
            if currentPosition > 90:
                if self.__currentSong and not self.__currentSongRecorded:
                    LOG.info('Soon finished. Recording stats and queuing '
                              'new  song...')
                    query = session.query(ChannelStat)
                    query = query.filter(
                            songTable.c.id == channelSongs.c.song_id)
                    query = query.filter(
                            songTable.c.id == self.__currentSong.id)
                    query = query.filter(
                            channelSongs.c.channel_id == self.id)
                    stat = query.first()
                    if not stat:
                        stat = ChannelStat(song_id=self.__currentSong.id,
                                           channel_id=self.id)
                        LOG.info("Setting last played date")
                        stat.lastPlayed = datetime.now()
                        stat.played = 1
                    else:
                        LOG.info("Updating last played date")
                        stat.lastPlayed = datetime.now()
                        stat.played = stat.played + 1
                    self.__currentSongRecorded = True
                    session.add(stat)
                    session.commit()

                    nextSong = self.getNextSong()
                    was_successful = self.queueSong(nextSong)
                    while not was_successful:
                        nextSong = self.getNextSong()
                        was_successful = self.queueSong(nextSong)

            # if we handed out credits more than 5mins ago, we give out some
            # more
            if (datetime.now() - lastCreditGiveaway).seconds > 300:
                LOG.info('Handing out credits to users.')
                maxCredits = int(Setting.get(
                    'max_credits',
                    '30',
                    channel_id=self.id))
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
