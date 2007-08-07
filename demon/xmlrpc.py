# -*- coding: utf-8 -*-
"""
XMLRpc-Service

If both settings "xmlrpc_port" and "xmlrpc_iface are set, this service will
automatically start up with the jukebox daemon.
"""
import SimpleXMLRPCServer, threading
from model import create_session, getSetting, Artist, Album, Song
from sqlalchemy import and_
from twisted.python import log

try:
   import simplejson
   if getSetting( 'xmlrpc_json', "1" ) == "1":
      jsonEnabled = True
   else:
      jsonEnabled = False
except:
   jsonEnabled = False

def marshal(data):
   """
   Defines how the data is marshalled before sending it over the wire.
   @type  data: str
   @param data: The data that is to be marshalled
   @return:     The marshalled data
   """
   if jsonEnabled:
      return simplejson.dumps( data )
   else:
      return data

class SatelliteAPI(object):
   """
   This class is bound to the XMLRpc service and contains the remotely
   accessible methods.
   """

   def __init__(self, jukebox):
      """
      Constructor.
      """
      self._jukebox = jukebox

   def help(self):
      """
      Returns the list of functions in this class
      """
      from types import FunctionType
      lst = [ (f,
               self.__getattribute__(f).__doc__
               ) for f in dir(self) if not f.startswith('_') ]
             #and type(self.__getattribute__(f)) == FunctionType
      return marshal(lst)

   def get_albums(self, artistName):
      """
      @type    artistName: str
      @param   artistName: The name of the artist
      @return: A list of albums of the named artist. Each item of the list is a
               tuple of the form "id, albumName".
      """
      sess = create_session()
      artist = sess.query(Artist).selectfirst_by(Artist.c.name==artistName)

      if artist is not None:
         output = [ (x.id, x.name) for x in artist.albums ]

      sess.close()
      return marshal(output)

   def get_album_songs( self, albumID ):
      """
      Returns a list of songs of the named album id.

      @type  albumID: int
      @param albumID: the database ID of the album
      @return: A list of songs of the named album. Each item of the list is a
               tuple of the form "id, song-title"
      """
      sess = create_session()
      album = sess.query(Album).selectfirst_by(Album.c.id == albumID)
      output = [ (a.id, a.title) for a in album.songs ]
      sess.close()
      return marshal(output)

   def ping(self):
      """
      A no-op. Useful to see if the xml-rpc service is running fine.

      @return: True
      """
      return marshal(True)

   def getCurrentSong(self, channelID):
      """
      Returns the currently playing song

      @type  channelID: int
      @param channelID: the channel-id

      @return: The ID of the playing song
      """

      return marshal(self._jukebox.getChannelByID(channelID).currentSong())

   def next(self, channelID):
      """
      Tells the channel to skip the current song.

      @type  channelID: int
      @param channelID: the channel-id

      @return: Success value
      """
      return marshal(self._jukebox.getChannelByID(channelID).skipSong())

   def play(self, channelID):
      """
      Tells the channel to begin playback.

      @type  channelID: int
      @param channelID: the channel-id

      @return: Success value
      """
      return marshal(self._jukebox.getChannelByID(channelID).startPlayback())

   def pause(self, channelID):
      """
      Tells the channel to pause playback.

      @type  channelID: int
      @param channelID: the channel-id

      @return: Success value
      """
      return marshal(self._jukebox.getChannelByID(channelID).pausePlayback())

   def stop(self, channelID):
      """
      Tells the channel to stop playback.

      @type  channelID: int
      @param channelID: the channel-id

      @return: Success value
      """
      return marshal(self._jukebox.getChannelByID(channelID).stopPlayback())

   def enqueue(self, channelID, songID, userID):
      """
      Enqueues a song.

      @type  channelID: int
      @param channelID: the channel-id

      @type  songID: int
      @param songID: The ID of the song

      @type  userID: int
      @param userID: The ID of the user
      """
      return marshal(self._jukebox.getChannelByID(channelID).enqueue(songID, userID))

   def moveup(self, channelID, queueID, delta):
      """
      Move a song higher up in the queue (meaning it's played earlier)

      @type  channelID: int
      @param channelID: the channel-id

      @type  queueID: int
      @param queueID: the queue-id

      @type  delta: int
      @param delta: the amount of steps to move an item in the queue
      """
      return marshal(self._jukebox.getChannelByID(channelID).moveup(queueID, delta))

   def movedown(self, channelID, queueID, delta):
      return marshal(self._jukebox.getChannelByID(channelID).movedown(queueID, delta))

   def movetop(self, queueID):
      pass

   def movebottom(self, queueID):
      pass

   def enqueue_album(self, albumID):
      pass

   def queue_delete(self, queueID):
      pass

   def queue_clear(self):
      pass

   def getSongData(self, songID):
      """
      Returns basic data of the named song
      @type  songID: int
      @param songID: The database-ID of the song
      @return: An dictionary (assoc. array) containing the elements "artist",
               "album" and "title". All of these are the literal values as
               strings (no IDs)
      """
      sess = create_session()
      song = sess.query(Song).selectfirst_by(Song.c.id == songID )
      output = None
      if song is not None:
         output = {
            'artist': song.artist.name,
            'album': song.album.name,
            'title': song.title
         }
      sess.close()
      return marshal(output)

   def get_songs(self, artist=None, artistID=None, album=None, albumID=None):
      """
      No clue what this method is supposed to do...
      TODO: figure it out!
      """
      sess = create_session()

      if artistID is not None:
         dbArtist = sess.query(Artist).selectfirst_by(Artist.c.id == artistID )
      elif artist is not None:
         dbArtist = sess.query(Artist).selectfirst_by(Artist.c.name==artistName)

      if albumID is not None:
         dbAlbum = sess.query(Album).selectfirst_by(Album.c.id == albumID )
      elif album is not None:
         dbAlbum = sess.query(Album).selectfirst_by(
               and_(Album.c.name == album, Album.c.artist_id == dbArtist.id ) )

      output = [ dbArtist.name, dbAlbum.name ]
      sess.close()
      return marshal(output)

class Satellite(threading.Thread):
   """
   The XML-Rpc service itself. None of these methods are exposed.
   """

   def __init__(self, jukebox):
      """
      @type  jukebox: Gatekeeper
      @param jukebox: The gatekeeper (central daemon) that controls all channels
      """
      self.port = getSetting( 'xmlrpc_port' )
      self.keepRunning = True
      if self.port == '':
         log.msg( '%-20s %20s %s' % ( 'XML-RPC support:', 'disabled', '(no port specified)' ) )
         self.keepRunning = False
         threading.Thread.__init__(self)
         return
      log.msg( '%-20s %30s' % ( 'XML-RPC support:', 'enabled' ) )

      self.ip   = getSetting( 'xmlrpc_iface', '127.0.0.1' )

      log.msg( "XML-RPC service starting up..." )
      while True:
         try:
            self.server = SimpleXMLRPCServer.SimpleXMLRPCServer((self.ip, int(self.port)))
            log.msg( '... done' )
            break;
         except:
            import time
            log.msg( "Retrying..." )
            time.sleep(1)
            pass

      self.server.register_instance(SatelliteAPI(jukebox))
      log.msg( "Serving XMLRPC on port %s" % self.port )
      threading.Thread.__init__(self)

   def run(self):
      "Main application loop"

      try:
         while self.keepRunning:
            self.server.handle_request()
      except:
         log.msg( 'Error in XMLRPC' )

   def stop(self):
      "Triggers the stopping of the service."
      if self.keepRunning == False:
         return
      log.msg( 'XMLRPC service stopped' )
      self.keepRunning = False

      # send a bogus request to the server, as the "handle_request" method is
      # blocking. So it it still there waiting for a final request.
      import xmlrpclib
      s = xmlrpclib.Server('http://%s:%s' % (self.ip, self.port))
      s.ping()
