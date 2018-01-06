"""
An interface to the music player daemon (mpd).
mpd is a client-server based audio player. It offers easy bindings to python
and hence it's a simple implementation
http://www.musicpd.org
"""

from datetime import datetime
import os, sys, time
import logging
logger = logging.getLogger(__name__)

from wickedjukebox.demon.lib import mpdclient
from wickedjukebox.demon.players import common
from wickedjukebox.demon.dbmodel import Setting


class Player(object):

    def __init__(self, id_, params):
       """
       Constructor
       Connects to the mpd-daemon.
       """
       from pprint import pprint
       pprint(params)
       # set up the connection to the daemon
       self.host = params['host']
       self.port = int(params['port'])
       self.root_folder = params['root_folder']
       self.song_started = None
       self.__connection = None

    def connect(self):
        """
        Connect to the mpd-player.
        """
        while True:
            try:
               logger.info( "Connecting to MPD backend..." )
               self.__connection = mpdclient.MpdController(self.host, self.port)
            except mpdclient.MpdConnectionPortError, ex:
               import traceback; traceback.print_exc()
               logger.warning("Error connecting to the player.")
               time.sleep(1)
               continue
            break
        logger.info( "... MPD connected" )

    def disconnect(self):
        "Disconnect from mpd-player"
        self.__connection = None

    def queue(self, args):
        """
        Appends a new song to the playlist, and removes the first entry in the
        playlist if it's becoming too large. This prevents having huge playlists
        after a while playing.

        @type  args: dict
        """
        filename = args['filename']
        # with MPD, filenames are relative to the path specified in the mpd
        # config!! This is handled here.
        if filename[0:len(self.root_folder)] == self.root_folder:
           filename = filename[len(self.root_folder)+1:]
        logger.info("queuing %r" % filename)
        added_files = []

        output = True
        try:
           added_files.extend(self.__connection.add([filename.encode('utf-8')]))
           if Setting.get('sys_utctime', 0) == 0:
              self.song_started = datetime.utcnow()
           else:
              self.song_started = datetime.now()
           if not added_files:
               logger.error( "error queuing (Probably not found in mpd).")
               output = False
           else:
               output = True
        except Exception, ex:
           logger.error( "error queuing (%s)." % ex )
           output = False

        # Crop Playlist
        self.crop_playlist(3)

        return output

    def start(self):
        """
        Starts playback
        """
        self.__connection.play()

    def stop(self):
        """
        Stops playback
        """
        self.__connection.stop()

    def crop_playlist(self, length=2):
        """
        Removes items from the *beginning* of the playlist to ensure it has only
        a fixed number of entries.

        @type  length: int
        @param length: The new size of the playlist
        """
        status = self.__connection.getStatus()
        if status.playlistLength <= length:
            # No cropping necessary
            return

        current_song = status.song
        if current_song < length-1:
            # We should not crop if we are playing inside the range we want to
            # crop
            return

        logger.debug('Cropping playlist from 0 to %s',
                     (current_song-1))

        self.__connection.delete([
            (0, current_song-1)
        ])

    def listeners(self):
        return []  # TODO

    def current_song(self):
        """
        Returns the currently running song
        """
        while True:
           try:
              if self.__connection.getCurrentSong() is False:
                 return None

              return os.path.join(
                    self.root_folder,
                    self.__connection.getCurrentSong().path.decode(sys.getfilesystemencoding()))
           except mpdclient.MpdError, ex:
              if str(ex).find('not done processing current command') > 0:
                 logger.warning('"not done processing current command" received. Retrying')
                 self.__connection.clearError()
                 time.sleep(1)
                 continue
              elif str(ex).find('playlistLength not found') > 0:
                 logger.warning('"playlistLength not found" received. Reconnecting to backend...')
                 __disconnect()
                 time.sleep(1)
                 __connect()
                 continue
              elif str(ex).find('problem parsing song info') > 0:
                 logger.warning('"problem parsing song info" received. Retrying')
                 self.__connection.clearError()
                 time.sleep(1)
                 continue
              else:
                 raise
           break

        return None

    def pause(self):
        """
        Pauses playback
        """
        self.__connection.pause()

    def position(self):
        """
        Returns the current position in the song. (currentSec, totalSec)
        """
        out = (0,0)
        try:
           pos = self.__connection.getSongPosition()
           if pos:
              out = (pos[0], pos[1])
           else:
              out = (0,0)
        except mpdclient.MpdError, ex:
           if str(ex).find('not done processing current command') > 0:
              pass
           else:
              raise

        if float(out[1]) == 0.0:
            return 0
        return (out[0] / float(out[1])) * 100

    def skip(self):
        """
        Skips the current song
        """
        self.__connection.next()

    def status(self):
        """
        Returns the status of the player (play, stop, pause)
        """
        while True:
           try:
              if self.__connection.getStatus().state == 1:
                 return common.STATUS_STOPPED
              elif self.__connection.getStatus().state == 2:
                 return common.STATUS_STARTED
              elif self.__connection.getStatus().state == 3:
                 return common.STATUS_PAUSED
              else:
                 return 'unknown (%s)' % self.__connection.getStatus().state
           except mpdclient.MpdError, ex:
              if str(ex).find('not done processing current command') > 0:
                 logger.debug("'Not done proc. command' error skipped")
                 time.sleep(1)
                 continue
              elif str(ex).find("playlistLength not found") > 0:
                 logger.debug("'playlistLength not found' error skipped")
                 time.sleep(1)
                 continue
              else:
                 try:
                    raise
                 except mpdclient.MpdStoredError:
                    return 'stop'
           break;

        return 'unknown'

    def upcoming_songs(self):
       """
       Returns songs which are queued after the current song
       """
       for i, entry in enumerate(self.__connection.playlist()):
           if i <= self.playlistPosition():
               continue
           yield {
               'album': entry.album,
               'artist': entry.artist,
               'path': entry.path,
               'title': entry.title,
           }

    def playlistPosition(self):
       """
       Returns the position in the playlist as integer
       """
       return self.__connection.status().song

    def playlistSize(self):
       """
       Returns the complete size of the playlist
       """
       return self.__connection.getStatus().playlistLength

    def clearPlaylist():
       """
       Clears the player's playlist
       """
       self.crop_playlist(0)

    def updatePlaylist(self):
       self.__connection.sendUpdateCommand()
