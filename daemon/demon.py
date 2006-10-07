import threading, logging
import time
import player
from util import *
from datetime import datetime

class Juggler(threading.Thread):
   """
   The Juggler is responsible for music playback. All changes of the playback
   (play, pause, skip, ...) have to be passed to the Juggler. It handles
   updating of the play statistics, and continuous playback. It manages the
   queue from the database and automatically adds new songs to the playlist. In
   case something is on the queue it takes off the next item, otherwise it
   picks a song at random.
   """

   __keepRunning     = True  # While this is true, the Juggler is alive
   __playStatus      = 'stopped'
   __currentSongID   = 0
   __currentSongFile = ''
   __predictionQueue = []
   __logger          = logging.getLogger('juggler')

   def __init__(self, channel):
      """
      Constructor

      Connects to the player and prepares the playlist

      PARAMETERS
         channel - the channel of this instance
      """
      threading.Thread.__init__(self)
      self.setName( '%s (%s)' % (self.getName(), 'juggler') )

      # setup song scoring coefficients
      self.__neverPlayed = int(getSetting('scoring_neverPlayed', 10))
      self.__playRatio   = int(getSetting('scoring_ratio',        4))
      self.__lastPlayed  = int(getSetting('scoring_lastPlayed',   7))
      self.__songAge     = int(getSetting('scoring_songAge',      0))

      # initialise the player
      self.__player  = player.createPlayer(channel.backend, channel.backend_params)
      self.__channel = channel

   def __dequeue(self):
      """
      Return the filename of the next item on the queue. If the queue is empty,
      pick one from the prediction queue
      """

      try:
         nextSong = list(QueueItem.select(orderBy=['added', 'position']))[0]
         filename = nextSong.song.localpath
         songID   = nextSong.song.id
         nextSong.destroySelf()
      except IndexError:
         # no item on the main queue. Use the internal prediction queue
         if len(self.__predictionQueue) == 0:
            self.__smartGet()
         nextSong = Songs.get( self.__predictionQueue.pop(0)[0] )
         filename = nextSong.localpath
         songID   = nextSong.id


      #TODO# The following is based on a wrong assumption of the "position" field.
      # This needs to be discussed!
      ## ok, we got the top of the queue. We can now shift the queue by 1
      ## This is a custom query. This is badly documented by SQLObject. Refer to
      ## the top comment in model.py for a reference
      #conn = QueueItem._connection
      #posCol = QueueItem.q.position.fieldName
      #updatePosition = conn.sqlrepr(
      #      Update(QueueItem.q,
      #         {posCol: QueueItem.q.position - 1} )) # this shifts
      #conn.query(updatePosition)
      #conn.cache.clear()
      #
      ## ok. queue is shifted. now drop all items having a position smaller than
      ## -6
      #delquery = conn.sqlrepr(Delete(QueueItem.q, where=(QueueItem.q.position < -6)))
      #conn.query(delquery)

      self.__player.queue(filename)

      return (songID, filename)

   def __smartGet(self):
      """
      determine a song that would be best to play next and add it to the
      prediction queue
      """

      query = """
         SELECT
            song_id,
            localpath,
            IFNULL( IF(played+skipped>=10, (played/(played+skipped))*%(playRatio)d, 0), 0)
               + (IFNULL( least(604800, time_to_sec(timediff(NOW(), lastPlayed))), 604800)-604800)/604800*%(lastPlayed)d
               + IF( played+skipped=0, %(neverPlayed)d, 0)
               + IFNULL( IF( time_to_sec(timediff(NOW(),added))<1209600, time_to_sec(timediff(NOW(),added))/1209600*%(songAge)d, 0), 0) score
         FROM songs
         ORDER BY score DESC, rand()
         LIMIT 0,10
      """ % {
         'neverPlayed': self.__neverPlayed,
         'playRatio':   self.__playRatio,
         'lastPlayed':  self.__lastPlayed,
         'songAge':     self.__songAge
      }

      # I won't use ORDER BY RAND() as it is way too dependent on the dbms!
      import random
      random.seed()
      conn = Songs._connection
      res = conn.queryAll(query)
      randindex = random.randint(1, len(res)) -1
      try:
         out = (res[randindex][0], res[randindex][1], float(res[randindex][2]))
         self.__logger.info("Selected song (%d, %s) via smartget. Score was %4.3f" % out)
         self.__predictionQueue.append(out)
      except IndexError:
         self.__logger.error('No song returned from query. Is the database empty?')
         pass

   def populatePlaylist(self):
      """
      First, this ensures the playlist does not grow too large. Then it checks
      if the current song is the last one playing. If that is the case, it will
      add a new song to the playlist.
      """

      self.__player.cropPlaylist()
      if self.__player.playlistPosition() == self.__player.playlistSize()-1 \
            or self.__player.playlistSize() == 0:
         try:
            # song is soon finished. Add the next one to the playlist
            nextSong = self.__dequeue()
            self.__currentSongID = nextSong[0]
            self.__player.queue(nextSong[1])
            self.__logger.info('queued %s' % nextSong[1])
         except IndexError:
            # no song in the queue run smartDj
            ##nextSong = self.__smartGet()
            ##self.__currentSongID = nextSong[0]
            ##self.__player.queue(nextSong[1])
            ##self.__logger.info('selected %s' % nextSong[1])
            pass

   def run(self):
      """
      The control loop of the Juggler
      Every x seconds (can be customised in the settings) it will check the
      position in the current song. If the song is nearly finished, it will
      take appropriate actions to ensure continuous playback (pick a song from
      the queue, or at random)
      """

      self.__logger.info('Started Juggler')
      cycle = int(getSetting('dj_cycle', '1'))

      lastCreditGiveaway = datetime.now()
      lastPing           = datetime.now()

      # while we are alive, do the loop
      while self.__keepRunning:

         # ping the database every 10 seconds
         if (datetime.now() - lastPing).seconds > 10:
            lastPing = datetime.now()
            self.__channel.ping = lastPing

         # check if the player accidentally went into the "stop" state
         if self.__player.status() == 'stop' and self.__playStatus == 'playing':
            self.__player.startPlayback()

         # or if it accidentally wen into the play state
         if self.__player.status() == 'play' and self.__playStatus == 'stopped':
            self.__player.stopPlayback()

         if self.__playStatus != 'playing':
            time.sleep(cycle)
            continue;

         # update "now playing" info
         if self.__currentSongFile != self.__player.getSong():
            try:
               self.__currentSongID   = list(Songs.selectBy(localpath = self.__player.getSong()))[0].id
               self.__currentSongFile = self.__player.getSong()
            except IndexError:
               print """
               bah %s 
               """ % self.__player.getSong()
               pass

         # if prediction queue is empty we add a new song to it
         if len(self.__predictionQueue) == 0:
            self.__smartGet()

         # if the song is soon finished, update stats and pick the next one
         currentPosition = self.__player.getPosition()
         if (currentPosition[1] - currentPosition[0]) == 3 or currentPosition == (0,0):
            if self.__currentSongID != 0:
               currentSong = Songs.get(self.__currentSongID)
               currentSong.lastPlayed = datetime.now()
               currentSong.played     = currentSong.played + 1
            self.__dequeue()

         # if we handed out credits more than 30mins ago, we give out some more
         if (datetime.now() - lastCreditGiveaway).seconds > 300:
            q = "UPDATE users SET credits=credits+5 WHERE credits<30"
            conn = Users._connection
            lastCreditGiveaway = datetime.now()
            conn.query(q)

         #old# # if the queue is empty, add a random song to the queue
         #old# if QueueItem.select().count() == 0:
         #old#    nextSong = Songs.get(self.__smartGet()[0])
         #old#    tmp = QueueItem(
         #old#          position=0,
         #old#          added=datetime.now(),
         #old#          song=nextSong,
         #old#          channel=1,
         #old#          user=Users.get(1)
         #old#          )
         #old#    self.populatePlaylist()
         #old#    self.__player.startPlayback()

         #old# # only queue new songs if we are in play-mode
         #old# if self.__playStatus == 'playing':

         #old#    # if the song is soon finished, update stats and pick the next one
         #old#    currentPosition = self.__player.getPosition()
         #old#    if (currentPosition[1] - currentPosition[0]) == 3 or currentPosition == (0,0):
         #old#       if self.__player.getSong():
         #old#          try:

         #old#             # retrieve info from the currently playing song
         #old#             # TODO: This is hardcoded for mpd. It HAS to be abstracted by
         #old#             #       the MPD class.
         #old#             cArtist = Artists.selectBy(name=self.__player.getSong().artist)[0]
         #old#             cAlbum  = Albums.selectBy(title=self.__player.getSong().album)[0]
         #old#             cTitle  = self.__player.getSong().title

         #old#             # I haven't figured out the way to add the album to the select
         #old#             # query. That's why I loop through all songs from a given artist
         #old#             # and title. It's highly unlikely though that there is more than
         #old#             # one entry.
         #old#             song = list(Songs.selectBy(artist=cArtist, title=cTitle, album=cAlbum))[0]
         #old#             song.lastPlayed = datetime.now()
         #old#             song.played = song.played + 1

         #old#          except IndexError, ex:
         #old#             # no song on the queue. We can ignore this error
         #old#             pass

         #old#       self.populatePlaylist()

         # wait for x seconds
         time.sleep(cycle)

      # self.__keepRunning became false. We should quit
      self.__logger.info('Stopped Juggler')

   def stop(self):
      """
      Requests the Juggler to cease operation and quit
      """
      self.__keepRunning = False

   def startPlayback(self):
      """
      Sends a "play" command to the player backend
      """
      self.__playStatus = 'playing'
      self.__player.startPlayback()
      return ('OK', 'OK')

   def stopPlayback(self):
      """
      Sends a "stop" command to the player backend
      """
      self.__playStatus = 'stopped'
      self.__player.stopPlayback()
      return ('OK', 'OK')

   def pausePlayback(self):
      """
      Sends a "pause" command to the player backend
      """
      if self.__playStatus == 'paused':
         self.__playStatus = 'playing'
      else:
         self.__playStatus = 'paused'
      self.__player.pausePlayback()
      return ('OK', 'OK')

   def skipSong(self):
      """
      Updates play statistics and sends a "next" command to the player backend
      """
      try:
         song = list(Songs.selectBy(localpath = self.__player.getSong()))[0]
         song.skipped = song.skipped + 1
      except IndexError, ex:
         # no song on the queue. We can ignore this error
         pass
      # set "current song" to the next in the queue
      self.__dequeue()
      self.__player.skipSong()
      return ('OK', 'OK')

   def playStatus(self):
      return ("OK", self.__playStatus)

   def nowPlaying(self):
      return ("OK", self.__currentSongID)


