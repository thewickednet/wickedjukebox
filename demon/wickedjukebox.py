import sys, os, threading, mutagen, time
from model import create_session, Artist, Album, Song, \
                  ChannelStat, Channel as dbChannel,\
                  getSetting, metadata as dbMeta,\
                  songTable, LastFMQueue, usersTable,\
                  Genre, genreTable
from sqlalchemy import and_
from datetime import datetime
from util import Scrobbler, fs_encoding
from twisted.python import log
import playmodes, players

def fsdecode( string ):
   try:
      return string.decode( fs_encoding )
   except UnicodeDecodeError:
      log.err( "Failed to decode %s using %s" % (`string`, fs_encoding) )
      return False

class Librarian(object):

   __activeScans = []

   class Scanner(threading.Thread):

      __abort = False
      __cap   = ''

      def abort(self):
         self.__abort = True

      def __init__(self, folders, args=None):
         if args is not None:
            self.__cap = args[0]
         self.__folders = folders
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
            log.err()
            return None

      def __crawl_directory(self, dir, cap=''):
         """
         Scans a directory and all its subfolders for media files and stores their
         metadata into the library (DB)

         PARAMETERS
            dir - the root directory from which to start the scan
            cap - limit crawling to the subset of <dir> starting with <cap>
                  so when scanning "/foo/bar" with a <cap> of 'ba' will scan:
                      /foo/bar/baz
                      /foo/bar/battery
                      /foo/bar/ba/nished
                  but not
                      /foo/bar/jane
         """
         if type(cap) != type( u'' ) and cap is not None:
            cap = cap.decode(fs_encoding)

         log.msg( "-------- scanning %s (cap='%s')---------" % (dir,cap) )

         # Only scan the files specified in the settings table
         recognizedTypes = getSetting('recognizedTypes', 'mp3 ogg flac').split()

         # count files
         log.msg( "-- counting..." )
         filecount = 0
         for root, dirs, files in os.walk(dir.encode(fs_encoding)):

            root = fsdecode(root)
            if root is False: continue

            for name in files:
               if type(name) != type( u'' ):
                  name = fsdecode(name)
                  if name is False: continue
               localname = os.path.join(root,name)[ len(dir)+1: ]
               if name.split('.')[-1] in recognizedTypes and localname.startswith(cap):
                  filecount += 1
               for x in dirs:
                  x = fsdecode(x)
                  if x is False: continue
                  if not x.startswith(cap): dirs.remove(x.encode(fs_encoding))

         # walk through the directories
         scancount  = 0
         errorCount = 0

         # TODO - getfilesystemencoding is *not* guaranteed to return the
         # correct encodings on *nix systems as the FS-encodings are not
         # enforced on these systems! It will crash here with a
         # UnicodeDecodeError if an unexpected encoding is found. Instead, it
         # should skip that file and print an print a useful message.
         totalcount = 0
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
                  totalcount += 1
                  try:
                     log.msg( "[%6d/%6d (%03.2f%%)] %s" % (
                        totalcount,
                        filecount,
                        totalcount/float(filecount)*100,
                        repr(os.path.basename(filename))
                        ))
                  except ZeroDivisionError:
                     log.msg( "[%6d/%6d (%5s )] %s" % (
                        totalcount,
                        filecount,
                        '?',
                        repr(os.path.basename(filename))
                        ))

                  try:
                     metadata = mutagen.File( filename )
                  except:
                     log.err( "%s contained no valid metadata!" % filename )
                     continue
                  title  = self.getTitle(metadata)
                  album  = self.getAlbum(metadata)
                  artist = self.getArtist(metadata)
                  assert( title is not None,
                        "Title cannot be empty! (file: %s)" % filename )
                  assert( artist is not None,
                        "Artist cannot be empty! (file: %s)" % filename )

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
                  filesize = os.stat(filename).st_size
                  bitrate  = self.getBitrate( metadata )

                  trackNo  = self.getTrack( metadata )
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
                  if session.query(Song).selectfirst_by( localpath=filename ) is None:

                     # it was not in the DB, create a newentry
                     song = Song( localpath = filename, artist=dbArtist, album=dbAlbum )
                     song.trackNo = trackNo
                     if genre is not None:
                        song.genres.append( genre )
                     song.title   = title
                     song.bitrate = bitrate
                     song.duration = duration
                     song.lastScanned = datetime.now()
                     song.filesize = filesize
                     session.save(song)
                     scancount += 1

                  else:
                     # we found the song in the DB. Load it so we can update it's
                     # metadata. If it has changed since it was added to the DB!
                     song = session.query(Song).selectfirst_by( localpath=filename )
                     if song.lastScanned is None \
                           or datetime.fromtimestamp(os.stat(filename).st_ctime) > song.lastScanned:

                        song.localpath   = filename
                        song.trackNo     = trackNo
                        song.title       = title
                        song.artist_id   = dbArtist.id
                        song.album_id    = dbAlbum.id
                        if genre is not None and genre not in song.genres:
                           song.genres      = []
                           song.genres.append( genre )
                        song.bitrate     = bitrate
                        song.filesize    = filesize
                        song.duration    = duration
                        song.lastScanned = datetime.now()
                        session.save(song)
                        log.msg( "Updated %s" % ( filename ) )
                        scancount += 1

                  try:
                     if song.title is not None \
                           and song.artist is not None \
                           and song.album is not None \
                           and song.trackNo != 0:
                        song.isDirty = False
                  except:
                     song.isDirty = True

            session.flush()
            session.close()

            # remove subdirectories from list that do not match the capping
            for x in dirs:
               x = fsdecode(x)
               if x is False: continue
               if not x.startswith(cap): dirs.remove(x.encode(fs_encoding))

         log.msg( "--- done scanning (%7d/%7d songs scanned, %7d errors)" % (scancount, filecount, errorCount) )

      def run(self):
         for folder in self.__folders:
            self.__crawl_directory(folder, self.__cap)

         session  = create_session()

         log.msg( "--- Checking for orphaned songs... " )
         for song in session.query(Song).select():
            if not os.path.exists(song.localpath):
               log.msg('File %s not found on filesystem.' % song.localpath)
               try:
                  targetSongs = session.query(Song).select(and_(
                        Song.c.title==song.title,
                        Song.c.artist_id==song.artist_id,
                        Song.c.album_id==song.album_id,
                        Song.c.track_no==song.track_no
                        ))

                  for targetSong in targetSongs:
                     if song.localpath != targetSong.localpath:
                        log.msg('Song with id %d moved to id %d' % (song.id, targetSong.id))
                        newPath = targetSong.localpath
                        for data in session.query(ChannelStat).select_by(ChannelStat.c.song_id==targetSong.id):
                           session.delete(data)
                        session.flush()
                        session.delete(targetSong)
                        song.localpath = newPath
                        session.save(song)
               except IndexError:
                  # no such song found. We can delete the entry from the database
                  log.msg('File %s disappeared!' % song.localpath)
                  for data in session.query(ChannelStat).select_by(song.c.song_id==song.id):
                     session.delete(data)
                  session.flush()
                  session.delete(song)
               session.flush()
         log.msg( "--- ... done checking for orphaned songs. " )

         log.msg( "--- Checking for empty genres... " )
         for x in session.query(Genre):
            if len(x.songs) == 0:
               log.msg('Genre %-15s was empty' % x.name)
               session.delete(x)
         session.flush()
         log.msg( "--- ... done checking for empty genres. " )

         log.msg( "--- Checking for empty albums... " )
         for x in session.query(Albums):
            if len(x.songs) == 0:
               log.msg('Album %-15s was empty' % x.name)
               session.delete(x)
         session.flush()
         log.msg( "--- ... done checking for empty albums. " )

         session.close()

   def __init__(self):
      pass

   def abortAll(self):
      for x in self.__activeScans:
         x.abort()

   def rescanLib(self, args=None):

      def direxists(dir):
         if not os.path.exists( dir ):
            log.err( "WARNING: '%s' does not exist!" % dir )
            return False
         else:
            return True


      mediadirs = [ x for x in getSetting('mediadir').split(' ') if direxists(x) ]

      if mediadirs != []:
         self.__activeScans.append( self.Scanner( mediadirs, args ) )
         self.__activeScans[-1].start()

class Channel(threading.Thread):

   __dbModel         = None
   __scrobbler       = None
   __keepRunning     = True
   __playStatus      = 'stopped'
   __currentSongID   = 0
   __currentSongRecorded = False
   __currentSongFile = ''
   __random          = None
   __queuemodel      = None

   name              = None

   def __init__(self, name):
      self.sess = create_session()
      self.__dbModel = self.sess.query(dbChannel).selectfirst_by( dbChannel.c.name == name )
      if self.__dbModel is not None:
         self.name = self.__dbModel.name
         log.msg( "Loaded channel %s" % self.__dbModel )
      else:
         log.err( "Failed to load channel from database. Please make sure that\
the named channel exists in the database table called 'channel'" )
         self.__keepRunning = False


      u = getSetting('lastfm_user', '', self.__dbModel.id)
      p = getSetting('lastfm_pass', '', self.__dbModel.id)
      if u == '' or p == '' or u is None or p is None:
         log.msg( '%-20s %20s %s' % ( 'lastFM support:', 'disabled', '(username or password empty)' ) )
      else:
         log.msg( '%-20s %20s' % ( 'lastFM support:', 'enabled' ) )
         self.__scrobbler = Scrobbler(u, p); self.__scrobbler.start()

      # initialise the player
      self.__player = players.create( self.__dbModel.backend, self.__dbModel.backend_params)

      self.sess.flush()
      threading.Thread.__init__(self)

   def currentSong(self):
      #song = self.sess.query(Song).selectfirst_by( Song.c.id == self.__currentSongID )
      return self.__currentSongID

   def isStopped(self):
      return self._Thread__stopped

   def close(self):
      log.msg( "Channel closing requested." )
      self.__player.stopPlayback()
      log.msg( "Syncronising channel" )
      self.sess.save( self.__dbModel )
      self.sess.flush()
      self.sess.close()
      log.msg( "Closing channel" )
      if self._Thread__started:
         self.__keepRunning = False

   def setBackend(self, backend):
      raise

   def startPlayback(self):
      self.__playStatus = 'playing'
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

   def skipSong(self):
      """
      Updates play statistics and sends a "next" command to the player backend
      """
      sess = create_session()
      stat = sess.query(ChannelStat).select( and_(
               songTable.c.id == ChannelStat.c.song_id,
               songTable.c.id == self.__currentSongID,
               ChannelStat.c.channel_id == self.__dbModel.id) )
      if stat == [] :
         stat = ChannelStat( songid = self.__currentSongID,
                             channelid = self.__dbModel.id)
         stat.skipped = 1
         stat.lastPlayed = datetime.now()
      else:
         stat = stat[0]
         stat.skipped = stat.skipped + 1
         stat.lastPlayed = datetime.now()
      sess.save(stat)
      sess.flush()
      sess.close()

      # set "current song" to the next in the queue or use random
      self.__random     = playmodes.create( getSetting( 'random_model', 'random_weighed' ) )
      self.__queuemodel = playmodes.create( getSetting( 'queue_model',  'queue_strict' ) )

      nextSong = self.__queuemodel.dequeue()
      if nextSong is None:
         nextSong = self.__random.get()
      log.msg( "[channel] skipping song" )
      self.__player.queue(nextSong.localpath.encode(fs_encoding))
      self.__player.cropPlaylist(1)
      self.__player.skipSong()

      return 'OK'

   def run(self):
      cycleTime = int(getSetting('channel_cycle', '1'))
      lastCreditGiveaway = datetime.now()
      lastPing           = datetime.now()
      sess               = create_session()

      # while we are alive, do the loop
      while self.__keepRunning:

         time.sleep(cycleTime)

         # ping the database every 10 seconds
         if (datetime.now() - lastPing).seconds > 10:
            lastPing = datetime.now()
            self.__dbModel.ping = lastPing

         # check if the player accidentally went into the "stop" state
         if self.__player.status() == 'stop' and self.__playStatus == 'playing':
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
                        songTable.c.id==self.__currentSongID,
                        ChannelStat.c.channel_id==self.__dbModel.id) )
               if stat == [] :
                  stat = ChannelStat( songid = self.__currentSongID,
                                      channelid = self.__dbModel.id)
                  stat.lastPlayed = datetime.now()
                  stat.played     = 1
               else:
                  stat = stat[0]
                  stat.lastPlayed = datetime.now()
                  stat.played     = stat.played + 1
               lfm = LastFMQueue( self.__currentSongID )
               sess.save(lfm)
               self.__currentSongRecorded = True
               sess.save(stat)
               sess.flush()

            # set "current song" to the next in the queue or use random
            self.__random     = playmodes.create( getSetting( 'random_model', 'random_weighed' ) )
            self.__queuemodel = playmodes.create( getSetting( 'queue_model',  'queue_strict' ) )

            nextSong = self.__queuemodel.dequeue()
            if nextSong is None:
               nextSong = self.__random.get()
            self.__player.queue(nextSong.localpath.encode(fs_encoding))
            self.__player.cropPlaylist(1)

         # if we handed out credits more than 5mins ago, we give out some more
         if (datetime.now() - lastCreditGiveaway).seconds > 300:
            usersTable.update(
                  usersTable.c.credits<30,
                  values={usersTable.c.credits: usersTable.c.credits+5}
                  ).execute( )
            lastCreditGiveaway = datetime.now()

         sess.flush()
         sess.close()

      log.msg( "Channel stopped" )

