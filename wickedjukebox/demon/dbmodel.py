# pylint: disable=no-member, attribute-defined-outside-init
# pylint: disable=too-few-public-methods, invalid-name
#
# SQLAlchemy mapped classes have their members injected by the Base metaclass.
# Pylint does not see those and causes false "no-member" messages. Which is why
# they are disabled in this module. The same goes for variable initialisation.
# Additionally, mapped classes don't necessarily have public methods.
# "invalid-name" is disabled because these variables don't really have the role
# of constants. Renaming them now would just produce even more unnecessary
# git-churn.

from __future__ import print_function

import logging
import sys
from datetime import date, datetime
from os import stat
from os.path import basename

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, MetaData,
                        String, Table, Unicode, create_engine)
from sqlalchemy.orm import mapper, relation, scoped_session, sessionmaker
from sqlalchemy.sql import insert, select, update
from wickedjukebox import load_config

LOG = logging.getLogger(__name__)
CFG = load_config()
DBURI = CFG.get('database', 'dsn')

metadata = MetaData()
engine = create_engine(DBURI, echo=False)
metadata.bind = engine
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

stateTable = Table(
    'state',
    metadata,
    autoload=True)
channelTable = Table(
    'channel',
    metadata,
    Column('name', Unicode(32)),
    Column('backend', Unicode(64)),
    Column('backend_params', Unicode()),
    autoload=True)
settingTable = Table(
    'setting',
    metadata,
    Column('value', Unicode()),
    autoload=True)
settingTextTable = Table(
    'setting_text',
    metadata,
    Column('comment', Unicode()),
    autoload=True)
artistTable = Table(
    'artist',
    metadata,
    Column('name', Unicode(128)),
    Column('added', DateTime, nullable=False, default=datetime.now),
    autoload=True)
albumTable = Table(
    'album',
    metadata,
    Column('name', Unicode(128)),
    Column('type', Unicode(32)),
    Column('added', DateTime, nullable=False, default=datetime.now),
    autoload=True)
songTable = Table(
    'song',
    metadata,
    Column('title', Unicode(128)),
    Column('localpath', Unicode(255)),
    Column('lyrics', Unicode()),
    Column('added', DateTime, nullable=False, default=datetime.now),
    autoload=True)
queueTable = Table(
    'queue',
    metadata,
    Column('added', DateTime, nullable=False, default=datetime.now),
    autoload=True)
channelSongs = Table('channel_song_data', metadata, autoload=True)
lastfmTable = Table('lastfm_queue', metadata, autoload=True)
usersTable = Table(
    'users',
    metadata,
    Column('added', DateTime, nullable=False, default=datetime.now),
    extend_existing=True,
    autoload=True)
dynamicPLTable = Table(
    'dynamicPlaylist',
    metadata,
    Column('label', Unicode(64)),
    Column('query', Unicode()),
    autoload=True)
song_has_genre = Table('song_has_genre', metadata, autoload=True)
genreTable = Table(
    'genre',
    metadata,
    Column('added', DateTime, nullable=False, default=datetime.now),
    extend_existing=True,
    autoload=True)
songStandingTable = Table('user_song_standing', metadata, autoload=True)
songStatsTable = Table('user_song_stats', metadata, autoload=True)
tagTable = Table('tag', metadata, autoload=True)
song_has_tag = Table(
    'song_has_tag',
    metadata,
    Column('song_id', Integer, ForeignKey('song.id')),
    Column('tag', String(32), ForeignKey('tag.label')),
)
shoutboxTable = Table(
    'shoutbox',
    metadata,
    Column('message', Unicode(255)),
)
groupsTable = Table('groups', metadata, autoload=True)


def caller_source():
    '''
    Returns the source line from the stack-frame *before* the call of
    *caller_source*.

    For example, if the stack is something like this::

        main()
            myfunction()
                my_inner_function()
                    source = caller_source()

    Then *source* will point to ``myfunction``!
    '''
    import traceback
    stack = traceback.extract_stack()
    source = stack[-2]
    return source


# ----------------------------------------------------------------------------
# Mappers
# ----------------------------------------------------------------------------


class Genre(object):

    def __init__(self, name):
        self.name = name
        self.added = datetime.now()

    def __repr__(self):
        return "<Genre %s name=%s>" % (self.id, repr(self.name))


class Tag(object):

    def __init__(self, label):
        self.label = label
        self.inserted = datetime.now()

    def __repr__(self):
        return "<Tag label=%r>" % (self.label)


class Setting(object):

    @classmethod
    def get(cls, param_in, default=None, channel_id=None, user_id=None):
        """
        Retrieves a setting from the database.

        @type  param_in:    str
        @param param_in:    The name of the setting as string
        @param default:     If it's set, it provides the default value in case
                            the value was not found in the database.
        @type  channel_id: int
        @param channel_id: The channel id if the setting is bound to a channel.
        @type  user_id:     int
        @param user_id:     The user id if the setting is bound to a user.
        """

        if LOG.isEnabledFor(logging.DEBUG):
            source = caller_source()
            LOG.debug("Retriveing setting %r for user %r and "
                      "channel %r with default: %r (source: %s:%s)...",
                      param_in, user_id, channel_id, default,
                      basename(source[0]), source[1])

        output = default

        try:
            query = select([settingTable.c.value])
            query = query.where(settingTable.c.var == param_in)

            if channel_id:
                query = query.where(settingTable.c.channel_id == channel_id)
            else:
                query = query.where(settingTable.c.channel_id == 0)

            if user_id:
                query = query.where(settingTable.c.user_id == user_id)
            else:
                query = query.where(settingTable.c.user_id == 0)

            result = query.execute()
            if result:
                setting = result.fetchone()

            # if a channel-setting was requested but no entry was found, we
            # fall back to a global setting
            if channel_id and not setting:
                LOG.debug("    No per-channel setting found. "
                          "Falling back to global setting...")
                return cls.get(param_in=param_in, default=default,
                               channel_id=None, user_id=user_id)

            if not setting:
                # The parameter was not found in the database. Do we have a
                # default?
                if default:
                    # yes, we have a default. Return that instead the database
                    # value.
                    LOG.debug("    Requested setting was not found! Returning "
                              "default value...")
                    output = default
                else:
                    LOG.debug("    Required parameter %s was not found in the "
                              "settings table!", param_in)
                    output = None

                try:
                    ins_q = insert(settingTable)
                    ins_q = ins_q.values({
                        'var': param_in,
                        'value': output,
                        'channel_id': channel_id or 0,
                        'user_id': user_id or 0})
                    ins_q.execute()
                    LOG.debug("    Inserted default value into the database!")
                except Exception:  # pylint: disable=broad-except
                    # catchall for graceful degradation
                    LOG.error("Unable to insert default setting into the "
                              "datatabase", exc_info=True)

            else:
                output = setting["value"]

            LOG.debug("    ... returning %r", output)
            return output

        except Exception as ex:  # pylint: disable=broad-except
            # MySQL raises some unhelpful exception classes. So we have to
            # inspect the error message instead and re-throw the exception if
            # the mesage is unknown.
            if str(ex).lower().find('connect') > 0:
                LOG.critical('Unable to connect to the database. Error was: '
                             '\n%s', ex)
                sys.exit(0)
            if str(ex).lower().find('exist') > 0:
                LOG.critical('Settings table not found. Did you create the '
                             'database tables?')
                sys.exit(0)
            else:
                # An unknown error occured. We raise it again
                raise


class Channel(object):

    def __repr__(self):
        return "<Channel %s name=%s>" % (self.id, repr(self.name))


class Artist(object):

    def __init__(self, name):
        self.name = name
        self.added = datetime.now()

    def __repr__(self):
        return "<Artist %s name=%s>" % (self.id, repr(self.name))


class State(object):

    @classmethod
    def set(cls, statename, value, channel_id=0):
        """
        Saves a state variable into the database

        @param statename: The variable name
        @param value : The value of the state variable
        @param channel_id: (optional) For channel based states, use this to set
                           the channel.
        """

        query = select([stateTable.c.state])
        query = query.where(stateTable.c.state == statename)
        query = query.where(stateTable.c.channel_id == channel_id)
        result = query.execute()
        if result and result.fetchone():
            # the state exists, we need to update it
            query = update(stateTable)
            query = query.values({'value': value, 'channel_id': channel_id})
            query = query.where(stateTable.c.state == statename)
            query = query.where(stateTable.c.channel_id == channel_id)
            query.execute()
        else:
            # unknown state, store it in the DB
            ins_q = insert(stateTable)
            ins_q = ins_q.values({
                'state': statename,
                'value': value,
                'channel_id': channel_id})
            ins_q.execute()

        if LOG.isEnabledFor(logging.DEBUG):
            source = caller_source()
            LOG.debug("State %r stored with value %r for channel %r "
                      "(from %s:%d)", statename, value, channel_id,
                      basename(source[0]), source[1])

    @classmethod
    def get(cls, statename, channel_id=0, default=None):
        """
        Retrieve a specific state.

        @param: The variable name
        @param: (optional) The channel id for states bound to a specific
                channel
        @param default: Return this value is the state is not found in the DB.
        @return: The state value
        """
        query = select([stateTable.c.value])
        query = query.where(stateTable.c.state == statename)
        query = query.where(stateTable.c.channel_id == channel_id)
        result = query.execute()
        if result:
            row = result.fetchone()
            if row:
                return row[0]
        if LOG.isEnabledFor(logging.WARNING):
            source = caller_source()
            LOG.warning("State %r not found for channel %r. "
                        "Returning %r (from %s:%d)",
                        statename, channel_id, default,
                        basename(source[0]), source[1])
        ins_q = insert(stateTable)
        ins_q = ins_q.values({
            'channel_id': channel_id,
            'state': statename,
            'value': default})
        ins_q.execute()
        LOG.debug("    Inserted default value into the database!")
        return default


class Album(object):

    def __init__(self, name, artist=None, artist_id=None, path=None):
        self.name = name
        if artist:
            self.artist_id = artist.id
        elif artist_id:
            self.artist_id = artist_id

        self.path = path
        self.added = datetime.now()

    def __repr__(self):
        return "<Album %s name=%s>" % (self.id, repr(self.name))


class Song(object):

    def __init__(self, localpath, artist, album):
        if localpath:
            self.localpath = localpath
        # if artist:
        #     self.artist_id = artist.id
        # if album:
        #     self.album_id  = album.id
        self.added = datetime.now()

    def __repr__(self):
        return "<Song id=%r artist_id=%r title=%r path=%r>" % (
            self.id, self.artist_id, self.title, self.localpath)

    def scan_from_file(self, localpath, encoding):
        """
        Scans a file on the disk and loads the metadata from that file

        @param localpath: The absolute path to the file
        @param encoding: The file system encoding
        """

        from os import path
        from wickedjukebox.model.audiometa import MetaFactory

        LOG.debug("Extracting metadata from %r", localpath)

        try:
            audiometa = MetaFactory.create(localpath.encode(encoding))
        except Exception:  # pylint: disable=broad-except
            # catchall for graceful-degradation
            LOG.warning("%r contained invalid metadata.",
                        localpath, exc_info=True)

        dirname = path.dirname(localpath.encode(encoding))

        self.__artistName = audiometa['artist']
        self.__genreName = (audiometa['genres'][0]
                            if audiometa['genres']
                            else None)
        self.__albumName = audiometa['album']
        self.localpath = localpath
        self.title = audiometa['title']
        self.duration = audiometa['duration']
        self.bitrate = audiometa['bitrate']
        self.track_no = audiometa['track_no']

        release_date = audiometa['release_date']
        if release_date:
            self.year = release_date.year

        try:
            self.filesize = stat(localpath.encode(encoding)).st_size
        except Exception:  # pylint: disable=broad-except
            # catchall for graceful-degradation
            LOG.warning('Unhandled Exception', exc_info=True)
            self.filesize = None

        self.artist_id = self.get_artist_id(self.__artistName)
        self.genre_id = self.get_genre_id(self.__genreName)
        self.album_id = self.get_album_id(dirname)
        self.lastScanned = datetime.now()

    def get_genre_id(self, genre_name):
        """
        If the genre already exists, return the ID of that genre, otherwise
        create a new instance

        @param genre_name: The name of the genre
        @return: The ID of the matching genre
        """

        testsel = select([genreTable.c.id])
        testsel = testsel.where(genreTable.c.name == genre_name)
        res = testsel.execute()
        row = res.fetchone()
        if row:
            return row[0]

        insq = insert(genreTable).values({
            'name': genre_name
        })
        result = insq.execute()
        return result.inserted_primary_key[0]

    def get_artist_id(self, artist_name):
        """
        If the artist already exists, return the ID of that artist, otherwise
        create a new instance

        @param artist_name: The name of the artist
        @return: The ID of the matching artist
        """

        testsel = select([artistTable.c.id])
        testsel = testsel.where(artistTable.c.name == artist_name)
        res = testsel.execute()
        row = res.fetchone()

        if row:
            return row[0]

        insq = insert(artistTable).values({
            'name': artist_name
        })
        result = insq.execute()
        return result.inserted_primary_key[0]

    def get_album_id(self, dirname):
        """
        If the album already exists, return the ID of that album, otherwise
        create a new instance

        @param dirname: The path where the files of this album are stored
        @return: The ID of the matching album
        """
        if not self.artist_id or not self.__albumName:
            LOG.warning("Unable to determine the album ID without a valid "
                        "artist_id and album-name!")

        artist_id = self.artist_id
        album_name = self.__albumName

        testsel = select([albumTable.c.id, albumTable.c.release_date])
        testsel = testsel.where(albumTable.c.path == dirname)
        row = testsel.execute().fetchone()

        album_id = None
        if row:
            album_id = row[0]

        if not album_id:
            data = {
                'name': album_name,
                'artist_id': artist_id,
                'path': dirname,
            }
            if self.year:
                data["release_date"] = date(self.year, 1, 1)

            insq = insert(albumTable).values(data)
            result = insq.execute()
            album_id = result.inserted_primary_key[0]

        # if this song's release date is newer than the album's release date,
        # we update the album release date
        if self.year and row:
            if ((row["release_date"] and
                 row["release_date"] < date(self.year, 1, 1)) or
                    (not row["release_date"] and self.year)):

                updq = update(albumTable)
                updq = updq.where(albumTable.c.path == dirname)
                updq = updq.values({'release_date': date(self.year, 1, 1)})
                updq.execute()

        return album_id

    def update_tags(self, api=None, session=None):
        """
        @raises: lastfm.error.InvalidApiKeyError
        """
        if not api:
            from wickedjukebox import lastfm
            api_key = getSetting.get("lastfm_api_key")
            LOG.warning("'update_tags' should be called with an instantiated "
                        "LastFM API instance to avoid unnecessary network "
                        "traffic!")
            api = lastfm.Api(api_key)
        if not self.title or not self.artist or not self.artist.name:
            LOG.error("Cannot update the tags for this song. Either artist or "
                      "track name are unknown")

        lastfm_track = api.get_track(
            artist=self.artist.name,
            track=self.title)
        current_tag_names = set([tag.label for tag in self.tags])
        lastfm_tag_names = set([tag.name for tag in lastfm_track.top_tags])

        if not session:
            # try to get the current session for this object
            session = Session.object_session(self)

        if not session:
            # unable to get a session
            return

        for remove_tag in current_tag_names.difference(lastfm_tag_names):
            LOG.debug("Removing tag %r from song %d", remove_tag, self.id)
            song_has_tag.delete().where(song_has_tag.c.tag == remove_tag)

        for add_tag in lastfm_tag_names.difference(current_tag_names):
            if len(add_tag) > 32:
                LOG.debug("WARNING: tag %r is too long!", add_tag)
                continue
            LOG.debug("Adding tag %r to song %d", add_tag, self.id)
            tag = Tag(add_tag)
            tag = session.merge(tag)
            self.tags.append(tag)


class QueueItem(object):

    def __init__(self):
        self.added = datetime.now()

    def __repr__(self):
        return "<QueueItem %s>" % (self.id)


class DynamicPlaylist(object):
    def __repr__(self):
        return "<DynamicPlaylist %s>" % (self.id)


class ChannelStat(object):
    def __init__(self, song_id, channel_id):
        self.song_id = song_id
        self.channel_id = channel_id


def getSetting(param_in, default=None, channel_id=None, user_id=None):
    source = caller_source()
    LOG.warning("DEPRECTAED: Please use Setting.get!\nSource: %s:%d --> %s",
                source[0], source[1], source[3])
    return Setting.get(param_in, default, channel_id, user_id)


def setState(statename, value, channel_id=0):
    source = caller_source()
    LOG.warning("DEPRECTAED: Please use Setting.set!\nSource: %s:%d --> %s",
                source[0], source[1], source[3])
    return State.set(statename, value, channel_id)


def getState(statename, channel_id=0):
    source = caller_source()
    LOG.warning("DEPRECTAED: Please use State.get!\nSource: %s:%d --> %s",
                source[0], source[1], source[3])
    return State.get(statename, channel_id)


mapper(State, stateTable, properties={
    # 'channel': relation(Channel)
})
mapper(Genre, genreTable)
mapper(Tag, tagTable)
mapper(ChannelStat, channelSongs)
mapper(DynamicPlaylist, dynamicPLTable)
mapper(QueueItem, queueTable, properties={
    'song': relation(Song)
})
mapper(Setting, settingTable)
mapper(Channel, channelTable)
mapper(Album, albumTable, properties=dict(
    songs=relation(Song, backref='album')))

mapper(Artist, artistTable, properties=dict(
    albums=relation(Album, backref='artist'),
    songs=relation(Song, backref='artist')
))
mapper(Song, songTable, properties=dict(
    channelstat=relation(ChannelStat, backref='song'),
    genres=relation(Genre, secondary=song_has_genre, backref='songs'),
    tags=relation(Tag, secondary=song_has_tag, backref='songs'),
))

if __name__ == "__main__":
    print(getSetting("test"))
