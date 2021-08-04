# pylint: disable=missing-docstring
#
# TODO This is currently a "work-in-progress". Documentation will be added as
# soon as it's feasible. In the mean-time, disabling this message allows for
# saner pylint output.

# pylint: disable=useless-object-inheritance
#
# This is still running on Python 2 so we need to inherit from "object" to get
# new-style classes.

# pylint: disable=invalid-name
#
# TODO This requires some names to be camel-case. This should be removed in the
# future, but then the "player" API must change as well.
"""
An interface to the music player daemon (mpd).
mpd is a client-server based audio player. It offers easy bindings to python
and hence it's a simple implementation
http://www.musicpd.org
"""

import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict

from wickedjukebox.adt import Song
from wickedjukebox.demon.lib import mpdclient
from wickedjukebox.demon.players import common

LOG = logging.getLogger(__name__)


class Player(object):

    def __init__(self, id_, params, sys_utctime=0):  # pylint: disable=unused-argument
        # type: (int, Dict[str, str], int) -> None
        """
        Constructor
        Connects to the mpd-daemon.
        """
        # set up the connection to the daemon
        self.host = params['host']
        self.port = int(params['port'])
        self.root_folder = params['root_folder']
        self.song_started = None
        self.sys_utctime = sys_utctime
        self.__connection = None

    @property
    def connection(self):
        return self.__connection

    def connect(self):
        # type: () -> None
        """
        Connect to the mpd-player.
        """
        while True:
            try:
                LOG.info("Connecting to MPD backend...")
                self.__connection = mpdclient.MpdController(
                    self.host, self.port)
            except mpdclient.MpdConnectionPortError:  # pragma: no cover
                LOG.warning("Error connecting to the player.", exc_info=True)
                time.sleep(1)
                continue
            break
        LOG.info("... MPD connected")

    def disconnect(self):
        # type: () -> None
        "Disconnect from mpd-player"
        self.__connection = None

    def queue(self, filename):
        # type: (str) -> bool
        """
        Appends a new song to the playlist, and removes the first entry in the
        playlist if it's becoming too large. This prevents having huge playlists
        after a while playing.

        @type  args: dict
        """
        # with MPD, filenames are relative to the path specified in the mpd
        # config!! This is handled here.
        if filename[0:len(self.root_folder)] == self.root_folder:
            filename = filename[len(self.root_folder)+1:]
        LOG.info("queuing %r", filename)
        added_files = []

        output = True
        try:
            mpd_response = self.__connection.add([filename.encode('utf-8')])
            added_files.extend(mpd_response)
            if self.sys_utctime == 0:
                self.song_started = datetime.utcnow()
            else:
                self.song_started = datetime.now()
            if not added_files:
                LOG.error("error queuing (Probably not found in mpd).")
                output = False
            else:
                output = True
        except Exception:  # pylint: disable=broad-except
            # catch-all for graceful degradation
            LOG.error("error queuing.", exc_info=True)
            output = False

        # Crop Playlist
        self.crop_playlist(3)

        return output

    def start(self):
        # type: () -> None
        """
        Starts playback
        """
        self.__connection.play()

    def stop(self):
        # type: () -> None
        """
        Stops playback
        """
        self.__connection.stop()

    def crop_playlist(self, length=2):
        # type: (int) -> None
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

        LOG.debug('Cropping playlist from 0 to %s',
                  (current_song-1))

        self.__connection.delete([
            (0, current_song-1)
        ])

    def listeners(self):  # pylint: disable=no-self-use
        return []  # TODO

    def current_song(self):
        # type: () -> Optional[str]
        """
        Returns the currently running song
        """
        while True:
            try:
                result = self.__connection.getCurrentSong()
                if result is False:
                    return None

                fs_encoding = sys.getfilesystemencoding()
                decoded = result.path.decode(fs_encoding)
                return os.path.join(self.root_folder, decoded)
            except mpdclient.MpdError as ex:
                if str(ex).find('not done processing current command') > 0:
                    LOG.warning('"not done processing current command" received. '
                                'Retrying')
                    self.__connection.clearError()
                    time.sleep(1)
                    continue
                elif str(ex).find('playlistLength not found') > 0:
                    LOG.warning('"playlistLength not found" received. '
                                'Reconnecting to backend...')
                    self.disconnect()
                    time.sleep(1)
                    self.connect()
                    continue
                elif str(ex).find('problem parsing song info') > 0:
                    LOG.warning(
                        '"problem parsing song info" received. Retrying')
                    self.__connection.clearError()
                    time.sleep(1)
                    continue
                else:
                    raise

    def pause(self):
        # type: () -> None
        """
        Pauses playback
        """
        self.__connection.pause()

    def position(self):
        # type: () -> float
        """
        Returns the current position in the song.
        """
        out = (0, 0)
        try:
            pos = self.__connection.getSongPosition()
            if pos:
                out = (pos[0], pos[1])
            else:
                out = (0, 0)
        except mpdclient.MpdError as ex:
            if str(ex).find('not done processing current command') > 0:
                pass
            else:
                raise

        if float(out[1]) == 0.0:
            return 0.0
        return (out[0] / float(out[1])) * 100

    def skip(self):
        # type: () -> None
        """
        Skips the current song
        """
        self.__connection.next()

    def status(self):
        # type: () -> str
        """
        Returns the status of the player (play, stop, pause)
        """
        while True:
            try:
                if self.__connection.getStatus().state == 1:
                    return common.STATUS_STOPPED
                if self.__connection.getStatus().state == 2:
                    return common.STATUS_STARTED
                if self.__connection.getStatus().state == 3:
                    return common.STATUS_PAUSED
                return 'unknown (%s)' % self.__connection.getStatus().state
            except mpdclient.MpdStoredError:
                return common.STATUS_STOPPED
            except mpdclient.MpdError as ex:
                if str(ex).find('not done processing current command') > 0:
                    LOG.debug("'Not done proc. command' error skipped")
                    time.sleep(1)
                    continue
                elif str(ex).find("playlistLength not found") > 0:
                    LOG.debug("'playlistLength not found' error skipped")
                    time.sleep(1)
                    continue
                raise

    def upcoming_songs(self):
        # type: () -> Generator[Song, None, None]
        """
        Returns songs which are queued after the current song
        """
        for i, entry in enumerate(self.__connection.playlist()):
            if i <= self.playlistPosition():
                continue
            yield Song(
                album=entry.album,
                artist=entry.artist,
                filename=entry.path,
                title=entry.title,
            )

    def playlistPosition(self):
        # type: () -> int
        """
        Returns the position in the playlist as integer
        """
        return self.__connection.status().song

    def playlistSize(self):
        # type: () -> int
        """
        Returns the complete size of the playlist
        """
        return self.__connection.getStatus().playlistLength

    def clearPlaylist(self):
        # type: () -> None
        """
        Clears the player's playlist
        """
        self.crop_playlist(0)

    def updatePlaylist(self):
        # type: () -> None
        self.__connection.sendUpdateCommand()
