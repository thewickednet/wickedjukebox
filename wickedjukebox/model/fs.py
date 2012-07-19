"""
Model for filesystem related code, including audio metadata.
"""
import logging

from mutagen import File as MutaFile
from datetime import datetime


def field_getter(field, single=False, converter=lambda x: x):
    """
    Creates a method to retrieve a field from an instance-field named 'meta'.
    If the named field does not exist, log a warning using the class-level
    logger named 'log' and return ``None``.

    The **meta** field should be a mutagen ``File`` instance. Or behave like
    one.

    Optionally, a field can be specified to return only a single value instead
    of a list (mutagen always returns lists).

    :param field: The field name.
    :type field: string
    :param single: Wether to return a single field or not.
    :type single: boolean
    :param converter: A function to convert values from the meta-tag *to* a
                      python object.
    :type converter: function
    """

    def the_getter(self):
        if not self.meta:
            self.__class__.log.error(u'No metadata available for {0}'.format(
                self.filename))
            return None
        if field not in self.meta:
            self.__class__.log.warning(
                u'No {field} value for {filename}!'.format(
                    field=field,
                    filename=self.filename))
            return None
        if single:
            return converter(self.meta[field][0])
        else:
            return converter(self.meta[field])
    return the_getter


def from_datestring(date):
    """
    Converts a date string to a datetime object.
    """
    if not date:
        return None

    if len(date) == 4:
        return datetime.strptime(date, '%Y')
    elif len(date) == 7:
        return datetime.strptime(date, '%Y-%m')
    elif len(date) == 10:
        return datetime.strptime(date, '%Y-%m-%d')
    else:
        raise ValueError('Unsupported date format for the value {0!r}'.format(
            date))


class File(object):

    log = logging.getLogger('{0}.File'.format(__name__))

    def __init__(self, filename, meta):
        """
        Constructor

        :param filename: The local filename.
        :param meta: The mutagen metadata.
        """
        if not isinstance(filename, unicode):
            File.log.warning(u'Consider passing filenames as unicode '
                    'instances!  This will allow the python interpreter to '
                    'do "the right thing" dealing with filename encodings. '
                    'This warning was triggered by the filename '
                    '{0!r}'.format(filename))

        self.meta = meta
        self.filename = filename

    artists = property(field_getter('artist'))
    albums = property(field_getter('album'))
    titles = property(field_getter('title'))
    length = property(field_getter('length', True))
    genres = property(field_getter('genres'))
    date = property(field_getter('date', True, converter=from_datestring))
    tracknumber = property(field_getter('tracknumber', True))

    def __repr__(self):
        return u'<File {0}>'.format(self.filename)

    @staticmethod
    def single_field(field):
        """
        In mutagen, the metadata fields always return lists of multiple
        values. For some fields this may not be "logical". In this case we
        return only the first value.

        :param field: The field which should only return one value
        """
        if not field:
            return None

        return field[0]

    @staticmethod
    def open(filename):
        File.log.debug(u'Opening {0}'.format(filename))
        meta = MutaFile(filename, easy=True)
        return File(filename, meta)


class Mediadir(object):
    """
    A class representing a media folder.
    """

    log = logging.getLogger('{0}.Mediadir'.format(__name__))

    def __init__(self, root):
        """
        Constructor

        :param root: The root folder for this media folder.
        """
        self.root = root

    def walk(self, processor=None, filter=None):
        """
        Walk through the root folder of this Mediadir, calling a processor
        function on all element.o

        :param processor: The function called on each element. The processor
                          should take one parameter: a
                          ``wickedjukebox.model.fs.File`` instance. It does
                          not need to return a value.
        :param filter: A function filtering entries. It should take one
                       parameter (the filename), and return eithr ``True`` or
                       ``False``. If it returns ``False``, the file will not
                       be processed.
        """
        if not filter:
            filter = lambda x: True

        if not processor:
            processor = lambda x: Mediadir.log.info(u'Dummy processor '
                    'for {0}'.format(x))

        from os import walk
        from os.path import join
        for root, dirs, files in walk(self.root):
            for fname in files:
                absname = join(root, fname)
                if not filter(absname):
                    continue
                processor(File.open(absname))
