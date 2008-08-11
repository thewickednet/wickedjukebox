import sys, os, threading, mutagen, time
from model import create_session, Artist, Album, Song, \
                  ChannelStat, Channel as dbChannel,\
                  getSetting, metadata as dbMeta,\
                  songTable, LastFMQueue, usersTable,\
                  State, setState, \
                  queueTable, Genre, genreTable
from sqlalchemy import and_
from datetime import datetime
from util import Scrobbler, fs_encoding
from twisted.python import log
import playmodes, players
from demon.util import config
from urllib2 import URLError
from random import choice, random

def fsdecode( string ):
   try:
      if type(string) == type(u''):
         print "%r is already a unicode object!" % (string)
         return string
      return string.decode( fs_encoding )
   except UnicodeDecodeError:
      import traceback; traceback.print_exc()
      print  "Failed to decode %s using %s" % (`string`, fs_encoding)
      return False

def fsencode( string ):
   try:
      return string.encode( fs_encoding )
   except UnicodeEncodeError:
      import traceback; traceback.print_exc()
      print  "Failed to encode %s using %s" % (`string`, fs_encoding)
      return False

def direxists(dir):
   if not os.path.exists( dir ):
      log.err( "WARNING: '%s' does not exist!" % dir )
      return False
   else:
      return True

class Scanner(threading.Thread):

      __abort     = False
      __cap       = ''
      __forceScan = False
      __total_files = 0
      __scanned_files = 0
      __callback  = None
      __errors    = []

      def abort(self):
         self.__abort = True

      def __init__(self, folders, args=None):

         if args is not None:
            self.__forceScan = args[0] != '0'
            try:
               self.__cap       = args[1]
            except IndexError:
               # no cap was specified. We can live with that
               import traceback; traceback.print_exc()
               pass

         self.__folders = folders
         self.__errors  = []
         threading.Thread.__init__(self)

      def getAlbum( self, meta ):
         if meta is None: return None
         if meta.has_key( 'TALB' ):
            return meta.get( 'TALB' ).text[0]
         elif meta.has_key( 'album' ):
            return meta.get('album')[0]
         return None

      def getArtist( self, meta ):
         if meta is None: return None
         if meta.has_key( 'TPE1' ):
            return meta.get( 'TPE1' ).text[0]
         elif meta.has_key( 'artist' ):
            return meta.get('artist')[0]
         return None

      def getTitle( self, meta ):
         if meta is None: return None
         if meta.has_key( 'TIT2' ):
            return meta.get( 'TIT2' ).text[0]
         elif meta.has_key( 'title' ):
            return meta.get('title')[0]
         # TDRC - year
         # musicbrainz_albumartist
         # title
         return None

      def getGenre( self, meta ):
         try:
            if meta.has_key( 'TCON' ):
               if meta.get( 'TCON' ).text[0] != '':
                  return meta.get( 'TCON' ).text[0]
         except:
            import traceback; traceback.print_exc()
            pass
         return None

      def getTrack(self, meta):
         if meta is None: return None
         if meta.has_key('TRCK'):
            return meta.get('TRCK').text[0].split('/')[0]
         else:
            if meta.get('tracknumber') is None:
               return None
            if type(meta.get('tracknumber')) == type([]):
               return meta.get('tracknumber')[0].split('/')[0]
            else:
               return meta.get('tracknumber').split('/')[0]
         return None

      def getDuration( self, meta ):
         if meta is None: return None
         if meta.info.length is None: return 0
         else: return meta.info.length

      def getBitrate(self, meta ):
         if meta is None: return None
         if 'audio/x-flac' in meta.mime: return None
         try:
            return meta.info.bitrate
         except AttributeError, ex:
            import traceback; traceback.print_exc()
            log.err()
            self.__errors.append("Error retrieving bitrate: %s", str(ex))
            return None

      def __crawl_directory(self, dir, cap='', forceScan=False):
         """
         Scans a directory and all its subfolders for media files and stores their
         metadata into the library (DB)

         @type  dir: str
         @param dir: the root directory from which to start the scan

         @type  cap: str
         $param cap: limit crawling to the subset of <dir> starting with <cap>
                     so when scanning "/foo/bar" with a <cap> of 'ba' will scan::

                        /foo/bar/baz
                        /foo/bar/battery
                        /foo/bar/ba/nished

                     but not::

                        /foo/bar/jane
         """
         if type(cap) != type( u'' ) and cap is not None:
            cap = cap.decode(fs_encoding)

         if not os.path.exists( dir.encode(fs_encoding) ):
            log.msg( "Folder '%s' not found!" % (dir) )
            return

         log.msg( "-------- scanning %s (cap='%s')---------" % (dir,cap) )

         # Only scan the files specified in the settings table
         recognizedTypes = getSetting('recognizedTypes', 'mp3 ogg flac').split()

         # count files
         log.msg( "-- counting..." )
         self.__total_files = 0
         for root, dirs, files in os.walk(dir.encode(fs_encoding)):

            root = fsdecode(root)
            if root is False: continue

            for name in files:
               if type(name) != type( u'' ):
                  name = fsdecode(name)
                  if name is False: continue
               localname = os.path.join(root,name)[ len(dir)+1: ]
               if name.split('.')[-1] in recognizedTypes and localname.startswith(cap):
                  self.__total_files += 1
               for x in dirs:
                  x = fsdecode(x)
                  if x is False: continue
                  if not x.startswith(cap): dirs.remove(x.encode(fs_encoding))

         # walk through the directories
         self.__scanned_files  = 0

         # TODO - getfilesystemencoding is *not* guaranteed to return the
         # correct encodings on *nix systems as the FS-encodings are not
         # enforced on these systems! It will crash here with a
         # UnicodeDecodeError if an unexpected encoding is found. Instead, it
         # should skip that file and print an print a useful message.
         self.__scanned_files = 0
         for root, dirs, files in os.walk(dir.encode(fs_encoding)):

            # if an abort is requested we exit right away
            if self.__abort is True: break;

            session  = create_session()
            root = fsdecode(root)
            if root is False: continue
            for name in files:
               if type(name) != type( u'' ):
                  name = fsdecode(name)
                  if name is False: continue
               filename = os.path.join(root,name)
               localname = os.path.join(root,name)[ len(dir)+1: ]
               if name.split('.')[-1] in recognizedTypes and localname.startswith(cap):
                  # we have a valid file
                  if config['core.debug'] != "0":
                     try:
                        log.msg( "[%6d/%6d (%03.2f%%)] %s" % (
                           self.__scanned_files,
                           self.__total_files,
                           self.__scanned_files/float(self.__total_files)*100,
                           repr(os.path.basename(filename))
                           ))
                     except ZeroDivisionError:
                        log.msg( "[%6d/%6d (%5s )] %s" % (
                           self.__scanned_files,
                           self.__total_files,
                           '?',
                           repr(os.path.basename(filename))
                           ))
                  elif self.__scanned_files % 1000 == 0:
                     log.msg("Scanned %d out of %d files" % (self.__scanned_files, self.__total_files))

                  try:
                     metadata = mutagen.File( filename.encode(fs_encoding) )
                  except Exception, ex:
                     import traceback; traceback.print_exc()
                     log.err( "%r contained no valid metadata! Excetion message: %s" % (filename, str(ex)) )
                     self.__errors.append( str(ex) )
                     continue
                  title  = self.getTitle(metadata)
                  album  = self.getAlbum(metadata)
                  artist = self.getArtist(metadata)
                  if title is None:
                     self.__errors.append( "Title of %r was empty! Not scanned!" % filename )
                     continue

                  if artist is None:
                     self.__errors.append( "Artist of  %r was empty! Not scanned!" % filename )
                     continue

                  dbArtist = session.query(Artist).selectfirst_by( name=artist )
                  if dbArtist is None:
                     dbArtist = Artist( name=artist )
                     session.save(dbArtist)
                     session.flush()

                  dbAlbum = session.query(Album).selectfirst_by( name=album )
                  if dbAlbum is None:
                     dbAlbum = Album( name=album, artist=dbArtist )
                     session.save(dbAlbum)
                     session.flush()

                  duration = self.getDuration( metadata )
                  filesize = os.stat(filename.encode(fs_encoding)).st_size
                  bitrate  = self.getBitrate( metadata )

                  track_no = self.getTrack( metadata )
                  title    = self.getTitle( metadata )
                  genreNm  = self.getGenre( metadata )
                  genre    = None
                  if genreNm is not None:
                     genre    = session.query(Genre).selectfirst_by( genreTable.c.name == genreNm )
                     if genre is None:
                        genre = Genre( name = genreNm )
                        session.save(genre)
                        session.flush()

                  # check if it is already in the database
                  song = session.query(Song).selectfirst_by( localpath=filename )
                  if song is None:

                     # it was not in the DB, create a new entry
                     song = Song( localpath = filename, artist=dbArtist, album=dbAlbum )
                     if genre is not None:
                        song.genres.append( genre )

                  else:
                     # we found the song in the DB. Load it so we can update it's
                     # metadata. If it has changed since it was added to the DB!
                     if forceScan \
                           or song.lastScanned is None \
                           or datetime.fromtimestamp(os.stat(filename.encode(fs_encoding)).st_ctime) > song.lastScanned:

                        song.localpath   = filename
                        song.artist_id   = dbArtist.id
                        song.album_id    = dbAlbum.id
                        if genre is not None and genre not in song.genres:
                           song.genres      = []
                           song.genres.append( genre )
                        if config['core.debug'] != "0":
                           log.msg( "Updated %s" % ( filename ) )

                  song.title       = title
                  song.track_no    = track_no
                  song.bitrate     = bitrate
                  song.duration    = duration
                  song.filesize    = filesize
                  song.lastScanned = datetime.now()
                  self.__scanned_files       += 1

                  try:
                     if song.title is not None \
                           and song.artist is not None \
                           and song.album is not None \
                           and song.track_no != 0:
                        song.isDirty = False
                  except:
                     import traceback; traceback.print_exc()
                     song.isDirty = True

                  session.save(song)

            session.flush()
            session.close()

            # remove subdirectories from list that do not match the capping
            for x in dirs:
               x = fsdecode(x)
               if x is False: continue
               if not x.startswith(cap): dirs.remove(x.encode(fs_encoding))

         log.msg( "--- done scanning (%7d/%7d songs scanned, %7d errors)" % (self.__scanned_files, self.__total_files, len(self.__errors)) )

      def run(self):
         for folder in self.__folders:
            self.__crawl_directory(folder, self.__cap, self.__forceScan)

         session  = create_session()

         #log.msg( "--- Checking for orphaned songs... " )
         #for song in session.query(Song).select():
         #   if not os.path.exists(song.localpath):
         #      log.msg('File %s not found on filesystem.' % song.localpath)
         #      try:
         #         targetSongs = session.query(Song).select(and_(
         #               Song.c.title==song.title,
         #               Song.c.artist_id==song.artist_id,
         #               Song.c.album_id==song.album_id,
         #               Song.c.track_no==song.track_no
         #               ))

         #         for targetSong in targetSongs:
         #            if song.localpath != targetSong.localpath:
         #               log.msg('Song with id %d moved to id %d' % (song.id, targetSong.id))
         #               newPath = targetSong.localpath
         #               for data in session.query(ChannelStat).select_by(ChannelStat.c.song_id==targetSong.id):
         #                  session.delete(data)
         #               session.flush()
         #               session.delete(targetSong)
         #               song.localpath = newPath
         #               session.save(song)
         #      except IndexError:
         #         # no such song found. We can delete the entry from the database
         #         log.msg('File %s disappeared!' % song.localpath)
         #         for data in session.query(ChannelStat).select_by(song.c.song_id==song.id):
         #            session.delete(data)
         #         session.flush()
         #         session.delete(song)
         #      session.flush()
         #log.msg( "--- ... done checking for orphaned songs. " )

         #log.msg( "--- Checking for empty genres... " )
         #for x in session.query(Genre):
         #   if len(x.songs) == 0:
         #      log.msg('Genre %-15s was empty' % x.name)
         #      session.delete(x)
         #session.flush()
         #log.msg( "--- ... done checking for empty genres. " )

         #log.msg( "--- Checking for empty albums... " )
         #for x in session.query(Albums):
         #   if len(x.songs) == 0:
         #      log.msg('Album %-15s was empty' % x.name)
         #      session.delete(x)
         #session.flush()
         #log.msg( "--- ... done checking for empty albums. " )

         session.close()
         if self.__callback is not None:
            self.__callback()

      def get_status(self):
         return {
            "total_files": self.__total_files,
            "scanned_files": self.__scanned_files,
            "errors": self.__errors,
            }

      def add_callback(self, func):
         self.__callback = func

class Librarian(object):

   __activeScans = []

   def __init__(self):
      pass

   def abortAll(self):
      for x in self.__activeScans:
         x.abort()

   def rescanLib(self, args=None):

      mediadirs = [ x for x in getSetting('mediadir').split(' ') if direxists(x) ]

      if mediadirs != []:
         self.__activeScans.append( Scanner( mediadirs, args ) )
         self.__activeScans[-1].start()

class Channel(threading.Thread):

   dbModel         = None
   __scrobbler       = None
   __keepRunning     = True
   __playStatus      = 'stopped'
   __currentSongID   = 0
   __currentSongRecorded = False
   __currentSongFile = ''
   __random          = None
   __queuemodel      = None
   __jingles_folder  = None
   __jingles_interval = 0
   __no_jingle_count = 0

   name              = None

   def __init__(self, name):
      self.sess = create_session()
      self.dbModel = self.sess.query(dbChannel).selectfirst_by( dbChannel.c.name == name )
      if self.dbModel is not None:
         self.name = self.dbModel.name
         log.msg( "Loaded channel %s" % self.dbModel )
      else:
         log.err( "Failed to load channel from database. Please make sure that\
the named channel exists in the database table called 'channel'" )
         self.__keepRunning = False


      u = getSetting('lastfm_user', '', self.dbModel.id)
      p = getSetting('lastfm_pass', '', self.dbModel.id)
      if u == '' or p == '' or u is None or p is None:
         log.msg( '%-20s %20s %s' % ( 'lastFM support:', 'disabled', '(username or password empty)' ) )
      else:
         log.msg( '%-20s %20s' % ( 'lastFM support:', 'enabled' ) )
         try:
            self.__scrobbler = Scrobbler(u, p); self.__scrobbler.start()
         except URLError:
            import traceback; traceback.print_exc()
            log.err("Unable to start scrobbler (internet down?)")

      # initialise the player
      self.__player = players.create( self.dbModel.backend, self.dbModel.backend_params)

      self.sess.flush()
      threading.Thread.__init__(self)

   def currentSong(self):
      res = queueTable.select( and_(
         queueTable.c.song_id == self.__currentSongID,
         queueTable.c.position == 0 ) ).execute()
      row = res.fetchone()

      userid = None
      if row is not None:
         userid = row[queueTable.c.user_id]

      return {"id": self.__currentSongID, "userid": userid }

   def isStopped(self):
      return self._Thread__stopped

   def close(self):
      log.msg( "Channel closing requested." )
      self.__player.stopPlayback()
      if config['core.debug'] != "0":
         log.msg( "Syncronising channel" )
      self.sess.save( self.dbModel )
      self.sess.flush()
      self.sess.close()
      log.msg( "Closing channel" )

      if self.__scrobbler is not None:
         self.__scrobbler.stop()

      if self._Thread__started:
         self.__keepRunning = False

   def setBackend(self, backend):
      raise

   def queueSong(self, song):

      if song.__class__.__name__ == "str":
         # we were passed a string. Most likely a file system path
         self.__player.queue(song)
         return
      elif song.__class__.__name__ == 'unicode':
         # we were passed a string. Most likely a file system path
         self.__player.queue(song.encode(fs_encoding))
         return

      sess = create_session()

      # update state in database
      setState( "current_song", song.id )

      # queue the song
      self.__player.queue(song.localpath.encode(fs_encoding))
      if self.__scrobbler is not None:
         a = sess.query(Artist).selectfirst_by(artist_id=song.artist_id)
         b = sess.query(Album).selectfirst_by(album_id=song.album_id)
         if a is not None and b is not None:
            try:
               self.__scrobbler.now_playing(artist=a.name,
                  track=song.title,
                  album=b.name,
                  length=int(song.duration),
                  trackno=int(song.track_no))
            except TypeError, ex:
               import traceback; traceback.print_exc()
               log.err(ex)
      sess.close()

   def startPlayback(self):
      self.__playStatus = 'playing'

      # TODO: This block is found as well in "skipSong! --> refactor"
      # set "current song" to the next in the queue or use random
      self.__random     = playmodes.create( getSetting( 'random_model', 'random_weighed' ) )
      self.__queuemodel = playmodes.create( getSetting( 'queue_model',  'queue_strict' ) )

      nextSong = self.__queuemodel.dequeue()
      if nextSong is None:
         nextSong = self.__random.get()

      # handle orphaned files
      while not os.path.exists(fsencode(nextSong.localpath)):
         log.err("%r not found!" % nextSong.localpath)
         nextSong = self.__random.get()

      self.queueSong(nextSong)

      self.__player.startPlayback()
      return 'OK'

   def pausePlayback(self):
      self.__playStatus = 'paused'
      self.__player.pausePlayback()
      return 'OK'

   def stopPlayback(self):
      self.__playStatus = 'stopped'
      self.__player.stopPlayback()
      return 'OK'

   def enqueue(self, songID, userID=None):

      self.__queuemodel = playmodes.create( getSetting( 'queue_model',  'queue_strict' ) )
      self.__queuemodel.enqueue(
            songID,
            userID,
            self.dbModel.id)
      return 'OK: queued song <%d> for user <%d> on channel <%d>' % (
            songID, userID, self.dbModel.id
            )

   def current_queue(self):
      self.__queuemodel = playmodes.create( getSetting( 'queue_model',  'queue_strict' ) )
      return self.__queuemodel.list()

   def skipSong(self):
      """
      Updates play statistics and sends a "next" command to the player backend
      """

      if self.__currentSongID is None or self.__currentSongID == 0:
         return

      sess = create_session()
      stat = sess.query(ChannelStat).select( and_(
               songTable.c.id == ChannelStat.c.song_id,
               songTable.c.id == self.__currentSongID,
               ChannelStat.c.channel_id == self.dbModel.id) )
      if stat == [] :
         stat = ChannelStat( songid = self.__currentSongID,
                             channelid = self.dbModel.id)
         stat.skipped = 1
         stat.lastPlayed = datetime.now()
      else:
         stat = stat[0]
         stat.skipped = stat.skipped + 1
         stat.lastPlayed = datetime.now()
      sess.save(stat)
      sess.flush()

      # TODO: This block is found as well in "startPlayback"! --> refactor"
      # set "current song" to the next in the queue or use random
      self.__random     = playmodes.create( getSetting( 'random_model', 'random_weighed' ) )
      self.__queuemodel = playmodes.create( getSetting( 'queue_model',  'queue_strict' ) )

      nextSong = self.__queuemodel.dequeue()
      if nextSong is None:
         nextSong = self.__random.get()
      if config['core.debug'] != "0":
         log.msg( "[channel] skipping song" )
      self.enqueue(nextSong.id)
      self.__player.cropPlaylist(2)
      self.__player.skipSong()
      sess.close()

      return 'OK'

   def moveup(self, qid, delta):
      self.__queuemodel = playmodes.create( getSetting( 'queue_model',  'queue_strict' ) )
      self.__queuemodel.moveup(qid, delta)

   def movedown(self, qid, delta):
      self.__queuemodel = playmodes.create( getSetting( 'queue_model',  'queue_strict' ) )
      self.__queuemodel.movedown(qid, delta)

   def get_jingle(self):
      self.__jingles_folder = getSetting('jingles_folder', None)
      self.__jingles_interval = getSetting('jingles_interval', None)
      if self.__jingles_interval == '':
         self.__jingles_interval = None
      elif self.__jingles_interval.find("-") > -1:
         jingle_boundary = [ int(x) for x in '-'.split(self.__jingles_interval) ]
      else:
         jingle_boundary = [ int(self.__jingles_interval), int(self.__jingles_interval) ]
      if self.__jingles_folder == '': self.__jingles_folder = None

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
               log.msg("No jingle count increased to %d" % self.__no_jingle_count)
         except OSError, ex:
            import traceback; traceback.print_exc()
            log.msg("Unable to open jingles: ", str(ex))

   def run(self):
      cycleTime = int(getSetting('channel_cycle', '3'))
      lastCreditGiveaway = datetime.now()
      lastPing           = datetime.now()
      sess               = create_session()

      # while we are alive, do the loop
      while self.__keepRunning:

         time.sleep(cycleTime)

         # ping the database every 10 seconds
         if (datetime.now() - lastPing).seconds > 10:
            lastPing = datetime.now()
            self.dbModel.ping = lastPing

         # check if the player accidentally went into the "stop" state
         if self.__player.status() == 'stop' and self.__playStatus == 'playing':
            # This most likely means we hit the end of the playlist:
            #   - clear the playlist
            #   - add the next song to the playlist and
            #   - start playback

            self.__player.cropPlaylist(0)

            self.__random     = playmodes.create( getSetting( 'random_model', 'random_weighed' ) )
            self.__queuemodel = playmodes.create( getSetting( 'queue_model',  'queue_strict' ) )

            nextSong = self.get_jingle()

            if nextSong is None:
               log.msg("No jingle selected. Trying to dequeue")
               nextSong = self.__queuemodel.dequeue()

            if nextSong is None:
               log.msg("Apparently there was nothing on the queue. I'm going to take somethin at random then")
               nextSong = self.__random.get()

            if nextSong is None:
               log.msg("What? Still nothing? This is bad. Maybe you should scan you media library first? I'll just sit here and wait then!")
               continue

            if nextSong.__class__.__name__ == "str" or nextSong.__class__.__name__ == "unicode":
               # we got a simple file. Not a tracked library song!
               self.queueSong(nextSong)
               self.__player.startPlayback()
            else:
               # handle orphaned files
               while not os.path.exists(fsencode(nextSong.localpath)):
                  log.err("%r not found!" % nextSong.localpath)
                  nextSong = self.__random.get()
               self.queueSong(nextSong)
               self.__player.startPlayback()

         # or if it accidentally wen into the play state
         if self.__player.status() == 'play' and self.__playStatus == 'stopped':
            self.__player.stopPlayback()

         # If we are not playing stuff, we can skip the rest
         if self.__playStatus != 'playing':
            continue;

         # -------------------------------------------------------------------
         if self.__currentSongFile != self.__player.getSong() \
               and self.__player.getSong() is not None:
            song = sess.query(Song).selectfirst_by( Song.c.localpath == self.__player.getSong() )
            if song is not None:
               self.__currentSongID       = song.id
            else:
               self.__currentSongID       = 0
            self.__currentSongRecorded = False
            self.__currentSongFile     = self.__player.getSong()

         # if the song is soon finished, update stats and pick the next one
         currentPosition = self.__player.getPosition()
         if (currentPosition[1] - currentPosition[0]) < 3:
            if self.__currentSongID != 0 and not self.__currentSongRecorded:
               stat = sess.query(ChannelStat).select( and_(
                        songTable.c.id == ChannelStat.c.song_id,
                        songTable.c.id == self.__currentSongID,
                        ChannelStat.c.channel_id==self.dbModel.id) )
               if stat == [] :
                  stat = ChannelStat( songid = self.__currentSongID,
                                      channelid = self.dbModel.id)
                  log.msg("Setting last played date")
                  stat.lastPlayed = datetime.now()
                  stat.played     = 1
               else:
                  stat = stat[0]
                  log.msg("Setting last played date")
                  stat.lastPlayed = datetime.now()
                  stat.played     = stat.played + 1
               lfm = LastFMQueue( self.__currentSongID, self.__player.songStarted)
               sess.save(lfm)
               self.__currentSongRecorded = True
               sess.save(stat)
               sess.flush()

         # if we handed out credits more than 5mins ago, we give out some more
         if (datetime.now() - lastCreditGiveaway).seconds > 300:
            maxCredits = int(getSetting('max_credits', '30'))
            usersTable.update(
                  usersTable.c.credits < maxCredits,
                  values={usersTable.c.credits: usersTable.c.credits+5}
                  ).execute( )
            lastCreditGiveaway = datetime.now()

         sess.flush()
         sess.close()

      log.msg( "Channel stopped" )

