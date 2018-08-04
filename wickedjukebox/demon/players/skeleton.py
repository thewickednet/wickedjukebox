# pylint: disable=invalid-name
#
# TODO This requires some names to be camel-case. This should be removed in the
# future, but then the "player" API must change as well.

# pylint: disable=unused-argument, no-self-use
#
# This is a "skeleton" file with empty implementations. Arguments are always
# unused.
"""
A no-op player interface. Use this as blueprint for new player interfaces.
"""


class Player(object):

    def __init__(self, id_, params):
        self.id_ = id_
        self.params = params

    def connect(self):
        pass  # no-op

    def config(self, params):
        """
        This method gets called right after loading the module. "params" is a
        dictionary created from the "backend_params" field in the channel-settings.
        """

        pass  # no-op

    def getPosition(self):
        """
        Returns the current position in the song. (currentSec, totalSec)
        """

        return (0, 0)

    def getSong(self):
        """
        Returns the full path to the currently running song
        """

        return None

    def playlistPosition(self):
        """
        Returns the position in the playlist as integer
        """
        return 0

    def queue(self, filename):
        """
        Appends a new song to the playlist, and removes the first entry in the
        playlist if it's becoming too large. This prevents having huge playlists
        after a while playing.

        @type  filename: str
        @param filename: The full path of the file
        """
        success = True
        return success

    def playlistSize(self):
        """
        Returns the complete size of the playlist
        """
        return 0

    def cropPlaylist(self, length=2):
        """
        Removes items from the *beginning* of the playlist to ensure it has only
        a fixed number of entries.

        @type  length: int
        @param length: The new size of the playlist
        """

        pass  # no-op

    def clearPlaylist(self):
        """
        Clears the player's playlist
        """
        cropPlaylist(0)

    def skipSong(self):
        """
        Skips the current song
        """

        pass  # no-op

    def stopPlayback(self):
        """
        Stops playback
        """

        pass  # no-op

    def pausePlayback(self):
        """
        Pauses playback
        """

        pass  # no-op

    def startPlayback(self):
        """
        Starts playback
        """

        pass  # no-op

    def status(self):
        """
        Returns the status of the player (play, stop, pause, unknown)
        """

        return 'unknown'

    def current_listeners(self):
        """
        Returns a list of unique identifiers of current listeners

        Return "None" if this feature is not supported or if the list of listeners is unknown
        """
        return []
