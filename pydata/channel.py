from demon.dbmodel import channelTable, Setting, Session, State, \
                          ChannelStat, Artist, Album, Song, \
                          usersTable, songTable, queueTable, channelSongs
from datetime import datetime
import time
import signal
from util import fsencode
import os
from random import choice, random
from sqlalchemy.sql import select, func, update
import demon.playmodes, demon.players
from threading import Thread

import logging
LOG = logging.getLogger(__name__)

class Channel(object):

   def handle_sigint(self, signal, frame):
      LOG.debug( "SIGINT caught" )
      self.close()

   def __init__(self, name):
      LOG.debug("Initialising channel...")

      self.id                    = None
      self.name                  = None
      self.__scrobbler           = None
      self.__keepRunning         = True
      self.__playStatus          = 'stopped'
      self.__currentSong         = None
      self.__currentSongRecorded = False
      self.__currentSongFile     = ''
      self.__randomstrategy      = None
      self.__queuestrategy       = None
      self.__jingles_folder      = None
      self.__jingles_interval    = 0
      self.__no_jingle_count     = 0
      self.__lastfm_api          = None
      self.last_tagged_song      = None

      lastfm_api_key = Setting.get( "lastfm_api_key", None )
      if lastfm_api_key:
         import lastfm
         self.__lastfm_api = lastfm.Api( lastfm_api_key )

      ##signal.signal(signal.SIGINT, self.handle_sigint)

      s = select([
         channelTable.c.id,
         channelTable.c.name,
         channelTable.c.backend,
         channelTable.c.backend_params,
         ])
      s = s.where( channelTable.c.name == name.decode("utf-8") )
      r = s.execute()
      self.__channel_data = r.fetchone()
      if not self.__channel_data:
         raise ValueError( "Failed to load channel %s from database. "
                       "Please make sure that the named channel exists "
                       "in the database table called 'channel'" % name )

      self.name = self.__channel_data["name"]
      LOG.debug( "Loaded channel %s" % self.name )

      self.__player = None
      self.id = self.__channel_data["id"]

   def currentSong(self):
      if not self.__currentSong:
         return None
      selq = select( [queueTable.c.user_id] )
      selq = selq.where( queueTable.c.song_id == self.__currentSong.id )
      selq = selq.where( queueTable.c.position == 0 )
      row  = selq.execute().fetchone()

      userid = None
      if row:
         userid = row["user_id"]

      return {"id": self.__currentSong.id, "userid": userid }

   def isStopped(self):
      return self.__playStatus == 'stopped'

   def close(self):
      LOG.debug( "Channel closing requested." )
      self.stopPlayback()

      LOG.debug( "Closing channel" )

      if self.__scrobbler is not None:
         self.__scrobbler.stop()
         self.__scrobbler.join()

      if self.__keepRunning:
         self.__keepRunning = False

   def setBackend(self, backend):
      raise NotImplementedError

   def queueSong(self, song):

      LOG.info( "Queueing %r" % fsencode(song) )

      if not self.__player:
         LOG.warning( "No player active. Won't queue %r" % song )
         return False

      if isinstance( song, unicode ):
         # we were passed a unicode string string. Most likely a file system path
         self.__player.queue(song)
         return True

      if isinstance( song, basestring ):
         # we were passed a string. Most likely a file system path
         self.__player.queue(fsdecode(song))
         return True

      session = Session()

      # update state in database
      State.set( "current_song", song.id, self.id )

      # queue the song
      self.__player.queue(song.localpath)
      if self.__scrobbler is not None:
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

   def __init_player(self):
      if not self.__player:
         self.__player = demon.players.create( self.__channel_data["backend"], self.__channel_data['backend_params'] + ", channel_id=%d" % self.id )

   def startPlayback(self):

      self.__init_player()

      self.__playStatus = 'playing'

      # TODO: This block is found as well in "skipSong! --> refactor"
      # TODO: The block to retrieve the next song should be a method in itself. Encapsulating queue, random and orphaned files
      # set "current song" to the next in the queue or use random
      self.__randomstrategy = demon.playmodes.create( Setting.get( 'random_model', 'random_weighed_prefetch', channel_id=self.id ) )
      self.__queuestrategy  = demon.playmodes.create( Setting.get( 'queue_model',  'queue_positioned',   channel_id=self.id ) )
      self.__randomstrategy.bootstrap( self.id )

      nextSong = self.__queuestrategy.dequeue(self.id)
      if not nextSong:
         nextSong = self.__randomstrategy.get(self.id)

      if nextSong is not None:
         # handle orphaned files
         while not os.path.exists(fsencode(nextSong.localpath)) and self.__keepRunning:
            LOG.error("%r not found!" % nextSong.localpath)
            songTable.update(songTable.c.id == nextSong.id, values={'broken': True}).execute()

            nextSong = self.__randomstrategy.get(self.id)

         self.queueSong(nextSong)

         self.__player.startPlayback()
         return 'OK'
      else:
         return 'ER: No song queued'

   def pausePlayback(self):
      self.__playStatus = 'paused'
      self.__player.pausePlayback()
      return 'OK'

   def stopPlayback(self):
      self.__playStatus = 'stopped'
      self.__player.stopPlayback()
      return 'OK'

   def enqueue(self, songID, userID=None):

      self.__queuestrategy = demon.playmodes.create( Setting.get( 'queue_model',  'queue_positioned', channel_id=self.id ) )
      self.__queuestrategy.enqueue(
            songID,
            userID,
            self.id)
      return 'OK: queued song <%d> for user <%d> on channel <%d>' % (
            songID, userID, self.id
            )

   def current_queue(self):
      self.__queuestrategy = demon.playmodes.create( Setting.get( 'queue_model',  'queue_positioned', channel_id=self.id ) )
      return self.__queuestrategy.list( self.id )

   def skipSong(self):
      """
      Updates play statistics and sends a "next" command to the player backend
      """

      if self.__currentSong is None:
         return

      session = Session()

      query = session.query(ChannelStat).select()
      query = query.filter( songTable.c.id == channelSongs.c.song_id )
      query = query.filter( songTable.c.id == self.__currentSong.id )
      query = query.filter( channelSongs.c.channel_id == self.id )
      stat = query.first()
      if not stat:
         stat = ChannelStat( songid = self.__currentSong.id,
                             channelid = self.id)
         stat.skipped = 1
         stat.lastPlayed = datetime.now()
      else:
         stat.skipped = stat.skipped + 1
         stat.lastPlayed = datetime.now()
      session.add(stat)

      # TODO: This block is found as well in "startPlayback"! --> refactor"
      # set "current song" to the next in the queue or use random
      self.__randomstrategy = demon.playmodes.create( Setting.get( 'random_model', 'random_weighed_prefetch', channel_id=self.id ) )
      self.__queuestrategy  = demon.playmodes.create( Setting.get( 'queue_model',  'queue_positioned', channel_id=self.id ) )
      self.__randomstrategy.bootstrap( self.id )

      nextSong = self.__queuestrategy.dequeue(self.id)
      if nextSong is None:
         nextSong = self.__randomstrategy.get(self.id)
      LOG.info( "[channel] skipping song" )

      session.close()
      if nextSong:
         self.enqueue(nextSong.id)
         self.__player.cropPlaylist(2)
         self.__player.skipSong()
         return 'OK'
      else:
         return 'ER: Unable to skip song, no followup song returned'

   def moveup(self, qid, delta):
      self.__queuestrategy = demon.playmodes.create( Setting.get( 'queue_model',  'queue_positioned', channel_id=self.id ) )
      self.__queuestrategy.moveup(self.id, qid, delta)

   def movedown(self, qid, delta):
      self.__queuestrategy = demon.playmodes.create( Setting.get( 'queue_model',  'queue_positioned', channel_id=self.id ) )
      self.__queuestrategy.movedown(self.id, qid, delta)

   def get_jingle(self):
      self.__jingles_folder = Setting.get('jingles_folder', default=None, channel_id=self.id)
      self.__jingles_interval = Setting.get('jingles_interval', default=None, channel_id=self.id)
      if self.__jingles_interval == '' or self.__jingles_interval is None:
         self.__jingles_interval = None
      elif self.__jingles_interval.find("-") > -1:
         jingle_boundary = [ int(x) for x in self.__jingles_interval.split("-") ]
      else:
         jingle_boundary = [ int(self.__jingles_interval), int(self.__jingles_interval) ]

      if self.__jingles_folder == '':
         self.__jingles_folder = None

      if (self.__jingles_interval is not None and self.__jingles_folder is not None):

         try:
            rnd = int(random()*(jingle_boundary[1]-jingle_boundary[0])) + self.__no_jingle_count
            if jingle_boundary[0] <= rnd:
               available_jingles = os.listdir( self.__jingles_folder )
               if available_jingles != []:
                  random_file = choice(available_jingles)
                  self.__no_jingle_count = 0
                  return os.path.join( self.__jingles_folder, random_file )
            else:
               self.__no_jingle_count += 1
               LOG.debug("No jingle count increased to %d" % self.__no_jingle_count)
         except OSError, ex:
            import traceback
            traceback.print_exc()
            LOG.warning("Unable to open jingles: %s" % str(ex))

   def update_current_listeners(self):
      "Scrape the Icecast admin page for current listeners and update theit state in the DB"
      listeners = self.__player.current_listeners()
      if listeners is None:
         # feature not supported by backedd player, or list of listeners unknwon
         return
      for l in listeners:
         usersTable.update(
            func.md5(usersTable.c.IP) == l,
            values={usersTable.c.proof_of_listening: func.now()}
            ).execute( )

   def process_upcoming_song(self):
      # A state "upcoming_song" with value -1 means that the upcoming song is
      # unwanted and a new one should be triggered if possible
      state = State.get( "upcoming_song", self.id )
      if state and int(state) == -1:
         LOG.debug( "Prefetching new song as the current upcoming_song was unwanted." )
         self.__randomstrategy.prefetch(self.id, async=False)

      if self.__randomstrategy:
         upcoming = self.__randomstrategy.peek(self.id)
         if upcoming:
            State.set( "upcoming_song", upcoming.id, self.id )
         else:
            State.set( "upcoming_song", None, self.id )
      else:
         State.set( "upcoming_song", None, self.id )

   def run(self):
      cycleTime = int(Setting.get('channel_cycle', default='3', channel_id=self.id))
      lastCreditGiveaway = datetime.now()
      lastPing           = datetime.now()
      proofoflife_timeout = int(Setting.get("proofoflife_timeout", 120))

      # while we are alive, do the loop
      while self.__keepRunning:

         time.sleep(cycleTime)
         self.process_upcoming_song()
         session = Session()

         self.__init_player()

         # ping the database every 2 minutes (unless another value was specified in the settings)
         if (datetime.now() - lastPing).seconds > proofoflife_timeout:
            self.update_current_listeners()
            lastPing = datetime.now()

            update( channelTable ).                   \
               where( channelTable.c.id == self.id ). \
               values( {'ping': datetime.now()} ).    \
               execute()

            proofoflife_timeout = int(Setting.get("proofoflife_timeout", 120))

         # check if the player accidentally went into the "stop" state
         if self.__player.status() == 'stop' and self.__playStatus == 'playing':
            # This most likely means we hit the end of the playlist:
            #   - clear the playlist
            #   - add the next song to the playlist and
            #   - start playback

            self.__player.cropPlaylist(0)

            self.__randomstrategy = demon.playmodes.create( Setting.get( 'random_model', 'random_weighed_prefetch', channel_id=self.id ) )
            self.__queuestrategy  = demon.playmodes.create( Setting.get( 'queue_model',  'queue_positioned',   channel_id=self.id ) )
            self.__randomstrategy.bootstrap( self.id )

            nextSong = self.get_jingle()

            if not nextSong:
               LOG.debug("No jingle selected. Trying to dequeue")
               nextSong = self.__queuestrategy.dequeue(self.id)

            if not nextSong:
               LOG.debug("Apparently there was nothing on the queue. I'm going to take somethin at random then")
               nextSong = self.__randomstrategy.get(self.id)

            if not nextSong:
               LOG.debug("What? Still nothing? Either nobody is online, or the database is empty")
               continue

            if isinstance( nextSong, basestring ):
               # we got a simple file. Not a tracked library song!
               self.queueSong(nextSong)
               self.__player.startPlayback()
            else:
               # handle orphaned files
               while not os.path.exists(fsencode(nextSong.localpath)) and self.__keepRunning:
                  LOG.error("%r not found!" % nextSong.localpath)
                  songTable.update(songTable.c.id == nextSong.id, values={'broken': True}).execute()
                  nextSong = self.__randomstrategy.get(self.id)
               self.queueSong(nextSong)
               self.__player.startPlayback()

         # or if it accidentally went into the play state
         if self.__player.status() == 'play' and self.__playStatus == 'stopped':
            self.__player.stopPlayback()

         skipState = State.get( "skipping", self.id )
         if skipState and int(skipState) == 1:
            State.set( "skipping", 0, self.id )
            self.__player.skipSong()

         # If we are not playing stuff, we can skip the rest
         if self.__playStatus != 'playing':
            continue

         # -------------------------------------------------------------------
         if self.__currentSongFile != self.__player.getSong() \
               and self.__player.getSong() is not None:
            song = session.query(Song).filter( songTable.c.localpath == self.__player.getSong() ).first()

            if song:
               self.__currentSong = song
            else:
               self.__currentSong = None

            self.__currentSongRecorded = False
            self.__currentSongFile     = self.__player.getSong()

         # update tags for the current song
         if self.last_tagged_song != self.__currentSong and self.__lastfm_api:
            pass #todo: currently disabled until it can be handled in a thread
            # try:
            #    self.__currentSong = session.merge(self.__currentSong)
            #    self.__currentSong.update_tags(self.__lastfm_api, session=session)
            #    session.commit()
            #    print self.__currentSong.tags
            # except Exception:
            #    LOG.error("Unable to update tags", exc_info=True)

         # if the song is soon finished, update stats and pick the next one
         currentPosition = self.__player.getPosition()
         if (currentPosition[1] - currentPosition[0]) < 3:
            if self.__currentSong and not self.__currentSongRecorded:
               query = session.query(ChannelStat)
               query = query.filter( songTable.c.id == channelSongs.c.song_id )
               query = query.filter( songTable.c.id == self.__currentSong.id )
               query = query.filter( channelSongs.c.channel_id == self.id )
               stat = query.first()
               if not stat:
                  stat = ChannelStat( song_id = self.__currentSong.id,
                                      channel_id = self.id)
                  LOG.debug("Setting last played date")
                  stat.lastPlayed = datetime.now()
                  stat.played     = 1
               else:
                  LOG.debug("Updating last played date")
                  stat.lastPlayed = datetime.now()
                  stat.played     = stat.played + 1
               self.__currentSongRecorded = True
               session.add(stat)
               session.commit()

         # if we handed out credits more than 5mins ago, we give out some more
         if (datetime.now() - lastCreditGiveaway).seconds > 300:
            maxCredits = int(Setting.get('max_credits', '30', channel_id=self.id ))
            usersTable.update(
                  usersTable.c.credits < maxCredits,
                  values={usersTable.c.credits: usersTable.c.credits+5}
                  ).execute( )
            # we may have overshot our target slightly. This fixes it
            usersTable.update(
                  usersTable.c.credits > maxCredits,
                  values={usersTable.c.credits: maxCredits}
                  ).execute( )
            lastCreditGiveaway = datetime.now()

         session.close()

      LOG.info( "Channel stopped" )

