# pylint: disable=missing-docstring, no-self-use, useless-object-inheritance
"""
Abstraction Layer for mutagen

Mutagen exposed the internal metadata as stored in the original file. This
causes an inconsistent external interface (f. ex. the "title" field is not
accessed in the same way for MP3 files as for FLAC files).

This module provides the necessary abstraction to handle all files identically

This modul is also executable and can be used to display meta information of a
specific file.
"""

import codecs
import logging
from datetime import date
from sys import stdout
from typing import List, TextIO

from mutagen import File
from mutagen.id3 import ID3TimeStamp
from mutagen.mp3 import MP3

# The class logger
LOG = logging.getLogger(__name__)

# Keys which are shared among different file types. Other filetypes may extend
# on this
WELL_KNOWN_KEYS = [
    "title",
    "artist",
    "comment",
    "release_date",
    "track_no",
    "total_tracks",
    "album",
    "genres",
    "duration",
    "bitrate",
]


class AudioMeta(dict):
    """
    Wraps Mutagen metadata and exposes it as a standardised dictionary
    """

    def __init__(self, mutagen_meta):
        """
        Initialises the class

        @param mutagen_meta: The mutagen metadata
        """
        self.meta = mutagen_meta
        self._keys = WELL_KNOWN_KEYS
        dict.__init__(self)

    def values(self):
        "@overrides dict.values"
        return [self.__getitem__(key) for key in self._keys]

    def keys(self):
        "@overrides dict.keys"
        return self._keys

    def items(self):
        "@overrides dict.items"
        return zip(list(self.keys()), list(self.values()))

    def __getitem__(self, key):
        "@overrides dict.__getitem__"
        accessor = self.__getattribute__("get_%s" % key)
        return accessor()

    def __len__(self):
        "@overrides dict.__len__"
        return len(self._keys)

    def __repr__(self):
        "@overrides dict.__repr__"
        reprdict = {}
        for key, value in self.items():
            reprdict[key] = value
        return reprdict.__repr__()

    # -------------------------------------------------------------------------

    def get_artist(self):
        return "Unimplemented meta-info"

    def get_title(self):
        return "Unimplemented meta-info"

    def get_release_date(self):
        return "Unimplemented meta-info"

    def get_comment(self):
        return "Unimplemented meta-info"

    def get_track_no(self):
        return "Unimplemented meta-info"

    def get_total_tracks(self):
        return "Unimplemented meta-info"

    def get_album(self):
        return "Unimplemented meta-info"

    def get_duration(self):
        return "Unimplemented meta-info"

    def get_genres(self):
        return ["Unimplemented meta-info"]

    def get_bitrate(self):
        return "Unimplemented meta-info"


class MP3Meta(AudioMeta):
    def decode_text(self, data):

        if isinstance(data.text[0], ID3TimeStamp):
            text = "".join([x.text for x in data.text])
        else:
            text = "".join(data.text)

        if data.encoding == 0:
            # latin-1
            return text

        if data.encoding == 1 or data.encoding == 2:
            # utf16 or utf16be
            encoded = text.encode("utf_16_le")
            if encoded.startswith(codecs.BOM_UTF16_BE) or encoded.startswith(
                codecs.BOM_UTF16_LE
            ):
                return encoded[2:].replace("\x00", "").decode("utf8")
            return text

        if data.encoding == 3:
            # utf8
            return text

        raise NotImplementedError(
            "Unknown character encoding (enoding=%s)" % data.encoding
        )

    def get_release_date(self):
        if "TDRC" not in self.meta:
            return None

        data = self.meta["TDRC"]
        raw_string = self.decode_text(data)
        elements = raw_string.split("-")

        try:
            if len(elements) == 1:
                return date(int(elements[0]), 1, 1)
            if len(elements) == 2:
                return date(int(elements[0]), int(elements[1]), 1)
            if len(elements) == 3:
                return date(
                    int(elements[0]), int(elements[1]), int(elements[2])
                )
        except ValueError as exc:
            LOG.warning("%s (datestring was %s)", exc, raw_string)
            return None

    def get_title(self):
        data = self.meta["TIT2"]
        return self.decode_text(data)

    def get_artist(self):
        return self.decode_text(self.meta["TPE1"])

    def get_track_no(self):
        tmp = self.decode_text(self.meta["TRCK"]).split("/")
        return int(tmp[0])

    def get_total_tracks(self):
        tmp = self.decode_text(self.meta["TRCK"]).split("/")
        if len(tmp) > 1:
            return int(tmp[1])
        return 0

    def get_album(self):
        return self.decode_text(self.meta["TALB"])

    def get_genres(self):
        try:
            return [self.decode_text(self.meta["TCON"])]
        except KeyError:
            return []

    def get_duration(self):
        return self.meta.info.length

    def get_bitrate(self):
        return self.meta.info.bitrate


class MetaFactory(object):
    # pylint: disable=too-few-public-methods
    """
    Factory to create the proper AudioMeta instance depending on filetype
    """

    @staticmethod
    def create(filename):
        try:
            mutagen_meta = File(filename)
        except IOError as exc:
            LOG.error(exc)
            return None

        if isinstance(mutagen_meta, MP3):
            abstract_meta = MP3Meta(mutagen_meta)
            return abstract_meta
        raise NotImplementedError(
            "This filetype (%s) is not yet implemented" % type(mutagen_meta)
        )


def display_file(filename, stream: TextIO = stdout):
    metadata = MetaFactory.create(filename)

    if metadata is None:
        return

    print(79 * "-", file=stream)
    print(filename, file=stream)
    print(79 * "-", file=stream)
    for key in metadata.keys():
        print("%-15s | %s" % (key, metadata[key]), file=stream)
    print(79 * "-", file=stream)


def main(argv: List[str], stream=stdout) -> int:
    logging.basicConfig()
    if len(argv) != 2:
        print(
            """Usage:
         %s <filename>
      """
            % argv[0],
            file=stream,
        )
        return 9
    display_file(argv[1], stream=stream)
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
