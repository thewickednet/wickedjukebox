# -*- coding: utf-8 -*-
"""
XMLRpc-API

This module contains the XML-RPC "Satellite" API. To activate the xml-rpc
interface all you need to do is set the port in the config.ini
"""
from model import create_session, getSetting, Artist, Album, Song
from sqlalchemy import and_

from twisted.python import log
from twisted.web import xmlrpc
import simplejson

class SatelliteAPI(xmlrpc.XMLRPC):
   """
   This class is bound to the XMLRpc service and contains the remotely
   accessible methods.
   """

   def __init__(self):
      """
      Constructor.
      """
      self.return_as_json = True

   def marshal(self, data):
      """
      Defines how the data is marshalled before sending it over the wire.
      @type  data: str
      @param data: The data that is to be marshalled
      @return:     The marshalled data
      """
      if self.return_as_json is True:
         return simplejson.dumps( data )
      else:
         return data

   def setGate( self, gate ):
      self._jukebox = gate

   def xmlrpc_help(self):
      """
      Returns the list of functions in this class
      """
      from types import FunctionType
      lst = [ (f,
               self.__getattribute__(f).__doc__
               ) for f in dir(self) if not f.startswith('_') ]
             #and type(self.__getattribute__(f)) == FunctionType
      return self.marshal(lst)

   def xmlrpc_get_albums(self, artistName):
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
      return self.marshal(output)

   def xmlrpc_get_album_songs( self, albumID ):
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
      return self.marshal(output)

   def xmlrpc_ping(self):
      """
      A no-op. Useful to see if the xml-rpc service is running fine.

      @return: True
      """
      return self.marshal(True)

   def xmlrpc_getCurrentSong(self, channelID):
      """
      Returns the currently playing song

      @type  channelID: int
      @param channelID: the channel-id

      @return: The ID of the playing song
      """

      if channelID is None or self._jukebox.getChannelByID(channelID) is None:
         return self.marshal(None)
      else:
         return self.marshal(self._jukebox.getChannelByID(channelID).currentSong())

   def xmlrpc_next(self, channelID):
      """
      Tells the channel to skip the current song.

      @type  channelID: int
      @param channelID: the channel-id

      @return: Success value
      """
      try:
         return self.marshal(self._jukebox.getChannelByID(channelID).skipSong())
      except Exception:
         LOG.exception('Unhandled exception')
         return False

   def xmlrpc_play(self, channelID):
      """
      Tells the channel to begin playback.

      @type  channelID: int
      @param channelID: the channel-id

      @return: Success value
      """
      return self.marshal(self._jukebox.getChannelByID(channelID).startPlayback())

   def xmlrpc_pause(self, channelID):
      """
      Tells the channel to pause playback.

      @type  channelID: int
      @param channelID: the channel-id

      @return: Success value
      """
      return self.marshal(self._jukebox.getChannelByID(channelID).pausePlayback())

   def xmlrpc_stop(self, channelID):
      """
      Tells the channel to stop playback.

      @type  channelID: int
      @param channelID: the channel-id

      @return: Success value
      """
      return self.marshal(self._jukebox.getChannelByID(channelID).stopPlayback())

   def xmlrpc_enqueue(self, channelID, songID, userID):
      """
      Enqueues a song.

      @type  channelID: int
      @param channelID: the channel-id

      @type  songID: int
      @param songID: The ID of the song

      @type  userID: int
      @param userID: The ID of the user
      """
      return self.marshal(self._jukebox.getChannelByID(channelID).enqueue(songID, userID))

   def xmlrpc_moveup(self, channelID, queueID, delta):
      """
      Move a song higher up in the queue (meaning it's played earlier)

      @type  channelID: int
      @param channelID: the channel-id

      @type  queueID: int
      @param queueID: the queue-id

      @type  delta: int
      @param delta: the amount of steps to move an item in the queue
      """
      return self.marshal(self._jukebox.getChannelByID(channelID).moveup(queueID, delta))

   def xmlrpc_movedown(self, channelID, queueID, delta):
      return self.marshal(self._jukebox.getChannelByID(channelID).movedown(queueID, delta))

   def xmlrpc_movetop(self, queueID):
      pass

   def xmlrpc_movebottom(self, queueID):
      pass

   def xmlrpc_enqueue_album(self, albumID):
      pass

   def xmlrpc_queue_delete(self, queueID):
      pass

   def xmlrpc_queue_clear(self):
      pass

   def xmlrpc_use_json(self, use_json):
      self.return_as_json = use_json
      return True

   def xmlrpc_getSongData(self, channelID, songID):
      """
      Returns basic data of the named song
      @param channelID: Channel ID
      @type  songID: int
      @param songID: The database-ID of the song (use -1 to retrieve the
                     current song data)
      @return: An dictionary (assoc. array) containing the elements "artist",
               "album" and "title". All of these are the literal values as
               strings (no IDs)
      """


      output = None
      if songID == -1:
         songID = self._jukebox.getChannelByID(channelID).currentSong()['id']

      sess = create_session()
      song = sess.query(Song).selectfirst_by(Song.c.id == songID )
      if song is not None:
         output = {
            'artist': song.artist.name,
            'album': song.album.name,
            'title': song.title
         }
      sess.close()
      return self.marshal(output)

   def xmlrpc_get_songs(self, artist=None, artistID=None, album=None, albumID=None):
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
      return self.marshal(output)

   def xmlrpc_current_queue(self, channelID):
      channel = self._jukebox.getChannelByID(channelID)
      if channel is not None:
         song_list = channel.current_queue()
         out = []
         if song_list is not None:
            for data in song_list:
               out.append(data)
         return self.marshal(out)
      else:
         return self.marshal( "ER: Error retrieving channel #%s" % channelID )

