# -*- coding: utf-8 -*-
"""
XMLRpc-API

This module contains the XML-RPC "Satellite" API. To activate the xml-rpc
interface all you need to do is set the port in the config.ini
"""
import logging

import simplejson
from model import Album, Artist, Song, create_session
from sqlalchemy import and_
from twisted.web import xmlrpc

LOG = logging.getLogger(__name__)


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
        self._jukebox = None

    def marshal(self, data):
        """
        Defines how the data is marshalled before sending it over the wire.
        @type  data: str
        @param data: The data that is to be marshalled
        @return:     The marshalled data
        """
        if self.return_as_json is True:
            return simplejson.dumps(data)
        return data

    def setGate(self, gate):
        self._jukebox = gate

    def xmlrpc_help(self):
        """
        Returns the list of functions in this class
        """
        from types import FunctionType
        lst = [(f,
                self.__getattribute__(f).__doc__
                ) for f in dir(self) if not f.startswith('_')]
        # and type(self.__getattribute__(f)) == FunctionType
        return self.marshal(lst)

    def xmlrpc_get_albums(self, artist_name):
        """
        @type    artist_name: str
        @param   artist_name: The name of the artist
        @return: A list of albums of the named artist. Each item of the list is a
                 tuple of the form "id, albumName".
        """
        sess = create_session()
        artist = sess.query(Artist).selectfirst_by(
            Artist.c.name == artist_name)

        if artist is not None:
            output = [(x.id, x.name) for x in artist.albums]

        sess.close()
        return self.marshal(output)

    def xmlrpc_get_album_songs(self, album_id):
        """
        Returns a list of songs of the named album id.

        @type  album_id: int
        @param album_id: the database ID of the album
        @return: A list of songs of the named album. Each item of the list is a
                 tuple of the form "id, song-title"
        """
        sess = create_session()
        album = sess.query(Album).selectfirst_by(Album.c.id == album_id)
        output = [(a.id, a.title) for a in album.songs]
        sess.close()
        return self.marshal(output)

    def xmlrpc_ping(self):
        """
        A no-op. Useful to see if the xml-rpc service is running fine.

        @return: True
        """
        return self.marshal(True)

    def xmlrpc_getCurrentSong(self, channel_id):
        """
        Returns the currently playing song

        @type  channel_id: int
        @param channel_id: the channel-id

        @return: The ID of the playing song
        """

        if channel_id is None or self._jukebox.getChannelByID(channel_id) is None:
            return self.marshal(None)
        return self.marshal(
            self._jukebox.getChannelByID(channel_id).currentSong())

    def xmlrpc_next(self, channel_id):
        """
        Tells the channel to skip the current song.

        @type  channel_id: int
        @param channel_id: the channel-id

        @return: Success value
        """
        try:
            return self.marshal(self._jukebox.getChannelByID(channel_id).skipSong())
        except Exception:  # pylint: disable=broad-except
            # catchall for graceful degradation
            LOG.exception('Unhandled exception')
            return False

    def xmlrpc_play(self, channel_id):
        """
        Tells the channel to begin playback.

        @type  channel_id: int
        @param channel_id: the channel-id

        @return: Success value
        """
        return self.marshal(self._jukebox.getChannelByID(channel_id).startPlayback())

    def xmlrpc_pause(self, channel_id):
        """
        Tells the channel to pause playback.

        @type  channel_id: int
        @param channel_id: the channel-id

        @return: Success value
        """
        return self.marshal(self._jukebox.getChannelByID(channel_id).pausePlayback())

    def xmlrpc_stop(self, channel_id):
        """
        Tells the channel to stop playback.

        @type  channel_id: int
        @param channel_id: the channel-id

        @return: Success value
        """
        return self.marshal(self._jukebox.getChannelByID(channel_id).stopPlayback())

    def xmlrpc_enqueue(self, channel_id, song_id, user_id):
        """
        Enqueues a song.

        @type  channel_id: int
        @param channel_id: the channel-id

        @type  song_id: int
        @param song_id: The ID of the song

        @type  user_id: int
        @param user_id: The ID of the user
        """
        return self.marshal(
            self._jukebox.getChannelByID(channel_id).enqueue(song_id, user_id))

    def xmlrpc_moveup(self, channel_id, queue_id, delta):
        """
        Move a song higher up in the queue (meaning it's played earlier)

        @type  channel_id: int
        @param channel_id: the channel-id

        @type  queue_id: int
        @param queue_id: the queue-id

        @type  delta: int
        @param delta: the amount of steps to move an item in the queue
        """
        return self.marshal(
            self._jukebox.getChannelByID(channel_id).moveup(queue_id, delta))

    def xmlrpc_movedown(self, channel_id, queue_id, delta):
        return self.marshal(
            self._jukebox.getChannelByID(channel_id).movedown(queue_id, delta))

    def xmlrpc_movetop(self, queue_id):
        pass

    def xmlrpc_movebottom(self, queue_id):
        pass

    def xmlrpc_enqueue_album(self, album_id):
        pass

    def xmlrpc_queue_delete(self, queue_id):
        pass

    def xmlrpc_queue_clear(self):
        pass

    def xmlrpc_use_json(self, use_json):
        self.return_as_json = use_json
        return True

    def xmlrpc_getSongData(self, channel_id, song_id):
        """
        Returns basic data of the named song
        @param channel_id: Channel ID
        @type  song_id: int
        @param song_id: The database-ID of the song (use -1 to retrieve the
                       current song data)
        @return: An dictionary (assoc. array) containing the elements "artist",
                 "album" and "title". All of these are the literal values as
                 strings (no IDs)
        """

        output = None
        if song_id == -1:
            song_id = self._jukebox.getChannelByID(
                channel_id).currentSong()['id']

        sess = create_session()
        song = sess.query(Song).selectfirst_by(Song.c.id == song_id)
        if song is not None:
            output = {
                'artist': song.artist.name,
                'album': song.album.name,
                'title': song.title
            }
        sess.close()
        return self.marshal(output)

    def xmlrpc_get_songs(self, artist=None, artist_id=None, album=None,
                         album_id=None):
        """
        No clue what this method is supposed to do...
        TODO: figure it out!
        """
        sess = create_session()

        if artist_id is not None:
            db_artist = sess.query(Artist).selectfirst_by(
                Artist.c.id == artist_id)
        elif artist is not None:
            db_artist = sess.query(Artist).selectfirst_by(
                Artist.c.name == artist.name)

        if album_id is not None:
            db_album = sess.query(Album).selectfirst_by(Album.c.id == album_id)
        elif album is not None:
            db_album = sess.query(Album).selectfirst_by(
                and_(Album.c.name == album, Album.c.artist_id == db_artist.id))

        output = [db_artist.name, db_album.name]
        sess.close()
        return self.marshal(output)

    def xmlrpc_current_queue(self, channel_id):
        channel = self._jukebox.getChannelByID(channel_id)
        if channel is not None:
            song_list = channel.current_queue()
            out = []
            if song_list is not None:
                for data in song_list:
                    out.append(data)
            return self.marshal(out)
        return self.marshal("ER: Error retrieving channel #%s" % channel_id)
