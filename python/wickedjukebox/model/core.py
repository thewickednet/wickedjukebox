"""
The core model of the application

This maps database tables to business classes.
"""

from sqlalchemy import (
        create_engine,
        Table,
        Column,
        MetaData,
        Unicode,
        DateTime,
        Integer,
        ForeignKey,
        String)
from sqlalchemy.sql import select, update, insert
from sqlalchemy.orm import mapper, sessionmaker, relation
from wickedjukebox.util.filesystem import load_config
from datetime import datetime, date
import sys
import logging
from os import stat
from os.path import basename

LOG = logging.getLogger(__name__)
CFG = load_config( "config.ini" )
DBURI = "%s://%s:%s@%s/%s?charset=utf8" % (
    CFG['database.type'],
    CFG['database.user'],
    CFG['database.pass'],
    CFG['database.host'],
    CFG['database.base'],
    )

METADATA = MetaData()
ENGINE = create_engine(DBURI, echo=False)
METADATA.bind = ENGINE
SESSION = sessionmaker( bind = ENGINE )

STATE_TABLE = Table( 'state', METADATA,
    autoload=True )

CHANNEL_TABLE = Table( 'channel', METADATA,
    Column( 'name', Unicode(32) ),
    Column( 'backend', Unicode(64) ),
    Column( 'backend_params', Unicode() ),
    autoload=True )

SETTING_TABLE = Table( 'setting', METADATA,
    Column( 'value', Unicode()),
    autoload=True )

SETTING_TEXT_TABLE = Table( 'setting_text', METADATA,
    Column( 'comment', Unicode()),
    autoload=True )

ARTIST_TABLE = Table( 'artist', METADATA,
    Column('name', Unicode(128)),
    Column( 'added', DateTime, nullable=False, default=datetime.now ),
    autoload=True )

ALBUM_TABLE = Table( 'album', METADATA,
    Column( 'name', Unicode(128) ),
    Column( 'type', Unicode(32) ),
    Column( 'added', DateTime, nullable=False, default=datetime.now ),
    autoload=True )

SONG_TABLE = Table( 'song', METADATA,
    Column( 'title', Unicode(128) ),
    Column( 'localpath', Unicode(255) ),
    Column( 'lyrics', Unicode() ),
    Column( 'added', DateTime, nullable=False, default=datetime.now ),
    autoload=True )

QUEUE_TABLE = Table( 'queue', METADATA,
    Column( 'added', DateTime, nullable=False, default=datetime.now ),
    autoload=True )

CHANNEL_SONGS_TABLE = Table( 'channel_song_data', METADATA, autoload=True )

LASTFM_TABLE = Table( 'lastfm_queue', METADATA, autoload=True )

USERS_TABLE = Table( 'users', METADATA,
    Column( 'added', DateTime, nullable=False, default=datetime.now ),
    useexisting=True,
    autoload=True )

DYNAMIC_PL_TABLE = Table( 'dynamicPlaylist', METADATA,
    Column( 'label', Unicode(64) ),
    Column( 'query', Unicode() ),
    autoload=True )

SONG_HAS_GENRE_TABLE = Table( 'song_has_genre', METADATA, autoload=True )

GENRE_TABLE = Table( 'genre', METADATA,
    Column( 'added', DateTime, nullable=False, default=datetime.now ),
    useexisting=True,
    autoload=True )

SONG_STANDING_TABLE = Table( 'user_song_standing', METADATA, autoload=True )

SONG_STATS_TABLE = Table( 'user_song_stats', METADATA, autoload=True )

TAG_TABLE = Table( 'tag', METADATA, autoload=True )

SONG_HAS_TAG = Table( 'song_has_tag', METADATA,
    Column('song_id', Integer, ForeignKey('song.id')),
    Column('tag', String(32), ForeignKey('tag.label')),
    )

# ----------------------------------------------------------------------------
# Mappers
# ----------------------------------------------------------------------------

class Genre(object):
    """
    A musical genre (could also be represented using tags!)
    """
    # pylint: disable=R0903

    def __init__(self, name):
        self.id = None # pylint: disable=C0103
        self.name = name
        self.added = datetime.now()

    def __repr__(self):
        return "<Genre %s name=%s>" % (self.id, repr(self.name))


class Tag(object):
    """
    A folksonomy tag
    """
    # pylint: disable=R0903

    def __init__(self, label):
        self.label = label
        self.inserted = datetime.now()

    def __repr__(self):
        return "<Tag label=%r>" % (self.label)


class Setting(object):
    """
    Convenience class to access application settings
    """
    # pylint: disable=R0903

    @classmethod
    def get(cls, param_in, default=None, channel_id=None, user_id=None):
        """
        Retrieves a setting from the database.

        @type  param_in: str
        @param param_in: The name of the setting as string
        @param default: If it's set, it provides the default value in case the
                        value was not found in the database.
        @type  channel_id: int
        @param channel_id: The channel id if the setting is bound to a channel.
        @type  user_id: int
        @param user_id: The user id if the setting is bound to a user.
        """

        if LOG.isEnabledFor( logging.DEBUG ):
            import traceback
            trace = traceback.extract_stack()
            source = trace[-2]
            LOG.debug("Retriveing setting %r for user %r and channel %r with "
                    "default: %r (source: %s:%s)..." % (
                        param_in, user_id, channel_id, default,
                        basename(source[0]), source[1] ))

        output = default

        try:
            query = select( [SETTING_TABLE.c.value] )
            query = query.where( SETTING_TABLE.c.var == param_in )

            if channel_id:
                query = query.where( SETTING_TABLE.c.channel_id == channel_id )
            else:
                query = query.where( SETTING_TABLE.c.channel_id == 0 )

            if user_id:
                query = query.where( SETTING_TABLE.c.user_id == user_id )
            else:
                query = query.where( SETTING_TABLE.c.user_id == 0 )

            result = query.execute()
            if result:
                setting = result.fetchone()

            # if a channel-setting was requested but no entry was found, we
            # fall back to a global setting
            if channel_id and not setting:
                LOG.debug("    No per-channel setting found. falling back to "
                        "global setting...")
                return cls.get(
                        param_in=param_in,
                        default=default,
                        channel_id=None,
                        user_id=user_id)

            if not setting:
                # The parameter was not found in the database. Do we have a
                # default?
                if default:
                    # yes, we have a default. Return that instead the database
                    # value.
                    LOG.debug("    Requested setting was not found! "
                            "Returning default value...")
                    output = default
                else:
                    LOG.debug( "    Required parameter %s was not found in "
                            "the settings table!" % param_in )
                    output = None

                try:
                    ins_q = insert( SETTING_TABLE )
                    ins_q = ins_q.values({
                        'var': param_in,
                        'value': output,
                        'channel_id': channel_id or 0,
                        'user_id': user_id or 0})
                    ins_q.execute()
                    LOG.debug("    Inserted default value into the databse!")
                except Exception:
                    LOG.error( "Unable to insert default setting into "
                            "the datatabase", exc_info=True )

            else:
                output = setting["value"]

            LOG.debug("    ... returning %r" % output)
            return output

        except Exception, ex:
            if str(ex).lower().find('connect') > 0:
                LOG.critical('Unable to connect to the database. '
                    'Error was: \n%s' % ex)
                sys.exit(0)
            if str(ex).lower().find('exist') > 0:
                LOG.critical('Settings table not found. Did you create '
                    'the database tables?')
                sys.exit(0)
            else:
                # An unknown error occured. We raise it again
                raise


class Channel(object):
    """
    A channel instance
    """
    # pylint: disable=R0903

    def __repr__(self):
        return "<Channel %s name=%s>" % (self.id, repr(self.name)) # pylint: disable=E1101, C0301


class State(object):
    """
    Represents the current state of the jukebox. The state variables are shared
    in this DB table.
    """

    @classmethod
    def set(cls, statename, value, channel_id=0):
        """
        Saves a state variable into the database

        @param statename: The variable name
        @param value     : The value of the state variable
        @param channel_id: (optional) For channel based states, use this to set
                                 the channel.
        """

        query = select( [STATE_TABLE.c.state] )
        query = query.where( STATE_TABLE.c.state == statename )
        query = query.where( STATE_TABLE.c.channel_id == channel_id )
        result = query.execute()
        if result and result.fetchone():
            # the state exists, we need to update it
            upd_q = update( STATE_TABLE )
            upd_q = upd_q.values( {'value': value, 'channel_id': channel_id} )
            upd_q = upd_q.where( STATE_TABLE.c.state == statename )
            upd_q = upd_q.where( STATE_TABLE.c.channel_id == channel_id )
            upd_q.execute()
        else:
            # unknown state, store it in the DB
            ins_q = insert( STATE_TABLE )
            ins_q = ins_q.values({
                'state': statename,
                'value': value,
                'channel_id': channel_id})
            ins_q.execute()

        if LOG.isEnabledFor( logging.DEBUG ):
            import traceback
            trace = traceback.extract_stack()
            source = trace[-2]
            LOG.debug("State %r stored with value %r for channel %r ("
                    "from %s:%d)" % (statename, value, channel_id, basename(
                        source[0]), source[1]))

    @classmethod
    def get(cls, statename, channel_id=0):
        """
        Retrieve a specific state

        @param: The variable name
        @param: (optional) The channel id for states bound to a specific channel
        @return: The state value
        """
        query = select( [STATE_TABLE.c.value] )
        query = query.where( STATE_TABLE.c.state == statename )
        query = query.where( STATE_TABLE.c.channel_id == channel_id )
        result = query.execute()
        if result:
            row = result.fetchone()
            if row:
                return row[0]
        if LOG.isEnabledFor( logging.WARNING ):
            import traceback
            trace = traceback.extract_stack()
            source = trace[-2]
            LOG.warn("State %r not found for channel %r (from %s:%d)" % (
                statename, channel_id, basename( source[0] ), source[1]))
        return None


class Album(object):
    """
    An album

    :param name: The album name
    :param artist: The artist of this album (default=None)
    :param artist_id: The artist ID (default=None)
    :param path: The folder containing files of this album (default=None)
    """
    # pylint: disable=R0903

    def __init__( self, name, artist=None, artist_id=None, path=None ):
        self.added = datetime.now()
        self.id = None # pylint: disable=C0103
        self.name = name
        self.path = path

        if artist:
            self.artist_id = artist.id
        elif artist_id:
            self.artist_id = artist_id

    def __repr__(self):
        return "<Album %s name=%s>" % (self.id, repr(self.name))


class Song(object):
    """
    A song instance

    :param localpath: The filesystem path
    :param artist: The artist of this song
    :param album: The album on which to find this song
    """

    def __init__( self, localpath, artist, album ):
        # pylint: disable=W0613

        self.__album_name = None
        self.__artist_name = None
        self.__genre_name = None
        self.added = datetime.now()
        self.album_id = None
        self.artist = None
        self.artist_id = None
        self.bitrate = None
        self.duration = None
        self.filesize = None
        self.genre_id = None
        self.id = None # pylint: disable=C0103
        self.last_scanned = None
        self.localpath = localpath
        self.tags = []
        self.title = None
        self.track_no = None
        self.year = None

        #if album:
        #    self.album_id  = album.id

        #if artist:
        #    self.artist_id = artist.id

    def __repr__(self):
        return "<Song id=%r artist_id=%r title=%r path=%r>" % (
                self.id, self.artist_id, self.title, self.localpath)

    def scan_from_file(self, localpath):
        """
        Scans a file on the disk and loads the metadata from that file

        @param localpath: The absolute path to the file
        @param encoding: The file system encoding
        """

        from os import path
        from audiometa import MetaFactory

        LOG.debug( "Extracting metadata from %r" % localpath )

        audiometa = MetaFactory.create(localpath)
        dirname = path.dirname(localpath)

        self.__artist_name = audiometa['artist']
        self.__genre_name = (len(audiometa['genres']) > 0 and
            audiometa['genres'][0] or
            None)
        self.__album_name = audiometa['album']
        self.localpath = localpath
        self.title = audiometa['title']
        self.duration = audiometa['duration']
        self.bitrate = audiometa['bitrate']
        self.track_no = audiometa['track_no']

        release_date    = audiometa['release_date']
        if release_date:
            self.year = release_date.year

        self.filesize = stat(localpath).st_size

        self.artist_id = self.get_artist_id( self.__artist_name )
        self.genre_id  = self.get_genre_id( self.__genre_name )
        self.album_id  = self.get_album_id(dirname)
        self.last_scanned = datetime.now()

    def get_genre_id( self, genre_name ):
        """
        If the genre already exists, return the ID of that genre, otherwise create a new instance

        @param genre_name: The name of the genre
        @return: The ID of the matching genre
        @todo: instead of using the mapped object "Genre" we could use the genreTable for performance gains
        """

        testsel = select( [GENRE_TABLE.c.id] )
        testsel = testsel.where( GENRE_TABLE.c.name == genre_name )
        res = testsel.execute()
        row = res.fetchone()
        if row:
            return row[0]

        insq = insert( GENRE_TABLE ).values({
                'name': genre_name
            })
        result = insq.execute()
        return result.last_inserted_ids()[0]

    def get_artist_id( self, artist_name ):
        """
        If the artist already exists, return the ID of that artist, otherwise create a new instance

        @param artist_name: The name of the artist
        @return: The ID of the matching artist
        @todo: This does not need to be an instance method of Song!
        """

        testsel = select( [ARTIST_TABLE.c.id] )
        testsel = testsel.where( ARTIST_TABLE.c.name == artist_name )
        res = testsel.execute()
        row = res.fetchone()

        if row:
            return row[0]

        insq = insert( ARTIST_TABLE ).values({
                'name': artist_name
            })
        result = insq.execute()
        return result.last_inserted_ids()[0]

    def get_album_id( self, dirname ):
        """
        If the album already exists, return the ID of that album, otherwise create a new instance

        @param dirname: The path where the files of this album are stored
        @return: The ID of the matching album
        @todo: This does not need to be an instance method of Song!
        """
        if not self.artist_id or not self.__album_name:
            LOG.warning("Unable to determine the album ID without a valid "
                    "artist_id and album-name!" )

        artist_id = self.artist_id
        album_name = self.__album_name

        testsel = select( [ALBUM_TABLE.c.id, ALBUM_TABLE.c.release_date] )
        testsel = testsel.where( ALBUM_TABLE.c.path == dirname )
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

            insq = insert( ALBUM_TABLE ).values(data)
            result = insq.execute()
            album_id = result.last_inserted_ids()[0]

        # if this song's release date is newer than the album's release date,
        # we update the album release date
        if self.year and row:
            if ((row["release_date"] and
                    row["release_date"] < date(self.year, 1, 1))
                or (not row["release_date"] and self.year)):

                updq = update( ALBUM_TABLE )
                updq = updq.where( ALBUM_TABLE.c.path == dirname )
                updq = updq.values({ 'release_date': date( self.year, 1, 1 ) })
                updq.execute()

        return album_id

    def update_tags(self, api=None, session=None):
        """
        @raises: lastfm.error.InvalidApiKeyError
        """
        if not api:
            import lastfm
            api_key = Setting.get( "lastfm_api_key", None )
            LOG.warning( "'update_tags' should be called with an "
                    "instantiated LastFM API instance to avoid "
                    "unnecessary network traffic!"
                    )
            api = lastfm.Api( api_key )
        if not self.title or not self.artist or not self.artist.name:
            LOG.error( "Cannot update the tags for this song. Either artist "
                    "or track name are unknown" )

        lastfm_track = api.get_track(
            artist = self.artist.name,
            track = self.title)
        current_tag_names = set([ tag.label for tag in self.tags ])
        lastfm_tag_names = set([ tag.name for tag in lastfm_track.top_tags ])

        if not session:
            # try to get the current session for this object
            session = SESSION.object_session(self)

        if not session:
            # unable to get a session
            return

        for remove_tag in current_tag_names.difference( lastfm_tag_names ):
            LOG.debug("Removing tag %r from song %d", (remove_tag, self.id) )
            SONG_HAS_TAG.delete().where( SONG_HAS_TAG.c.tag == remove_tag )

        for add_tag in lastfm_tag_names.difference(current_tag_names):
            if len(add_tag) > 32:
                LOG.debug( "WARNING: tag %r is too long!" % (add_tag) )
                continue
            LOG.debug( "Adding tag %r to song %d" % (add_tag, self.id) )
            tag = Tag(add_tag)
            tag = session.merge(tag)
            self.tags.append(tag)


class DynamicPlaylist(object):
    """
    A dynamic playlist
    """
    # pylint: disable=R0903

    def __repr__(self):
        return "<DynamicPlaylist %s>" % (self.id) # pylint: disable=E1101


class ChannelStat(object):
    """
    Statistics for a channel
    """
    # pylint: disable=R0903

    def __init__( self, song_id, channel_id ):
        self.song_id = song_id
        self.channel_id = channel_id


class Artist(object):
    """
    An artist
    """
    # pylint: disable=R0903

    def __init__( self, name ):
        self.name  = name
        self.added = datetime.now()

    def __repr__(self):
        return "<Artist %s name=%s>" % (self.id, repr(self.name)) # pylint: disable=E1101,C0301


class QueueItem(object):
    """
    An Song in the current Queue
    """
    # pylint: disable=R0903

    def __init__(self):
        self.added = datetime.now()

    def __repr__(self):
        return "<QueueItem %s>" % (self.id) # pylint: disable=E1101


mapper( State, STATE_TABLE, properties={
    ##'channel': relation(Channel)
})
mapper( Genre, GENRE_TABLE )
mapper( Tag, TAG_TABLE )
mapper( ChannelStat, CHANNEL_SONGS_TABLE )
mapper( DynamicPlaylist, DYNAMIC_PL_TABLE )
mapper(QueueItem, QUEUE_TABLE, properties={
    'song': relation(Song)
})
mapper(Setting, SETTING_TABLE)
mapper(Channel, CHANNEL_TABLE)
mapper(Album, ALBUM_TABLE, properties=dict(
    songs=relation(Song, backref='album')))

mapper(Artist, ARTIST_TABLE, properties=dict(
    albums= relation(Album, backref='artist'),
    songs = relation(Song,  backref='artist')
    ))
mapper(Song, SONG_TABLE, properties=dict(
    channelstat=relation( ChannelStat, backref='song' ),
    genres = relation( Genre, secondary=SONG_HAS_GENRE_TABLE, backref='songs' ),
    tags = relation( Tag, secondary=SONG_HAS_TAG, backref='songs' ),
    ))

