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


import logging
from base64 import b64encode
from datetime import date, datetime
from os import path, stat, urandom
from os.path import basename
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Unicode,
    create_engine,
    func,
)
from sqlalchemy.orm import Session as TSession
from sqlalchemy.orm import mapper, relation, scoped_session, sessionmaker
from sqlalchemy.sql import insert, select, update

from wickedjukebox.config import load_config
from wickedjukebox.model.audiometa import MetaFactory

LOG = logging.getLogger(__name__)
CFG = load_config()
DBURI = CFG.get("database", "dsn")

#: sentinel object to mark settings with no explicit default
NO_DEFAULT = object()

metadata = MetaData()
engine = create_engine(DBURI, echo=False)
metadata.bind = engine
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

stateTable = Table("state", metadata, autoload=True)
channelTable = Table(
    "channel",
    metadata,
    Column("name", Unicode(32)),
    Column("backend", Unicode(64)),
    Column("backend_params", Unicode()),
    autoload=True,
)
settingTable = Table(
    "setting", metadata, Column("value", Unicode()), autoload=True
)
settingTextTable = Table(
    "setting_text", metadata, Column("comment", Unicode()), autoload=True
)
artistTable = Table(
    "artist",
    metadata,
    Column("name", Unicode(128)),
    Column("added", DateTime, nullable=False, default=datetime.now),
    autoload=True,
)
albumTable = Table(
    "album",
    metadata,
    Column("name", Unicode(128)),
    Column("type", Unicode(32)),
    Column("added", DateTime, nullable=False, default=datetime.now),
    autoload=True,
)
songTable = Table(
    "song",
    metadata,
    Column("title", Unicode(128)),
    Column("localpath", Unicode(255)),
    Column("lyrics", Unicode()),
    Column("added", DateTime, nullable=False, default=datetime.now),
    autoload=True,
)
queueTable = Table(
    "queue",
    metadata,
    Column("added", DateTime, nullable=False, default=datetime.now),
    autoload=True,
)
channelSongs = Table("channel_song_data", metadata, autoload=True)
lastfmTable = Table("lastfm_queue", metadata, autoload=True)
usersTable = Table(
    "users",
    metadata,
    Column("added", DateTime, nullable=False, default=datetime.now),
    extend_existing=True,
    autoload=True,
)
dynamicPLTable = Table(
    "dynamicPlaylist",
    metadata,
    Column("label", Unicode(64)),
    Column("query", Unicode()),
    autoload=True,
)
song_has_genre = Table("song_has_genre", metadata, autoload=True)
genreTable = Table(
    "genre",
    metadata,
    Column("added", DateTime, nullable=False, default=datetime.now),
    extend_existing=True,
    autoload=True,
)
songStandingTable = Table("user_song_standing", metadata, autoload=True)
songStatsTable = Table("user_song_stats", metadata, autoload=True)
tagTable = Table("tag", metadata, autoload=True)
song_has_tag = Table(
    "song_has_tag",
    metadata,
    Column("song_id", Integer, ForeignKey("song.id")),
    Column("tag", String(32), ForeignKey("tag.label")),
)
shoutboxTable = Table(
    "shoutbox",
    metadata,
    Column("message", Unicode(255)),
)
groupsTable = Table("groups", metadata, autoload=True)


def caller_source():
    """
    Returns the source line from the stack-frame *before* the call of
    *caller_source*.

    For example, if the stack is something like this::

        main()
            myfunction()
                my_inner_function()
                    source = caller_source()

    Then *source* will point to ``myfunction``!
    """
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

    @staticmethod
    def by_name(name: str) -> Optional["Genre"]:
        session = Session()
        query = session.query(Genre).filter_by(name=name)
        return query.one_or_none()


class Tag(object):
    def __init__(self, label):
        self.label = label
        self.inserted = datetime.now()

    def __repr__(self):
        return "<Tag label=%r>" % (self.label)


class Channel(object):
    def __init__(self, name, backend, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.backend = backend

    def __repr__(self):
        return "<Channel %s name=%s>" % (self.id, repr(self.name))


class Artist(object):
    def __init__(self, name):
        self.name = name
        self.added = datetime.now()

    def __repr__(self):
        return "<Artist %s name=%s>" % (self.id, repr(self.name))

    @staticmethod
    def by_name(
        name: str, session: Optional[TSession] = None
    ) -> Optional["Artist"]:
        session = session or Session()
        query = session.query(Artist).filter_by(name=name)
        return query.one_or_none()


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
            query = query.values({"value": value, "channel_id": channel_id})
            query = query.where(stateTable.c.state == statename)
            query = query.where(stateTable.c.channel_id == channel_id)
            query.execute()
        else:
            # unknown state, store it in the DB
            ins_q = insert(stateTable)
            ins_q = ins_q.values(
                {"state": statename, "value": value, "channel_id": channel_id}
            )
            ins_q.execute()

        if LOG.isEnabledFor(logging.DEBUG):
            source = caller_source()
            LOG.debug(
                "State %r stored with value %r for channel %r " "(from %s:%d)",
                statename,
                value,
                channel_id,
                basename(source[0]),
                source[1],
            )

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
            LOG.warning(
                "State %r not found for channel %r. "
                "Returning %r (from %s:%d)",
                statename,
                channel_id,
                default,
                basename(source[0]),
                source[1],
            )
        ins_q = insert(stateTable)
        ins_q = ins_q.values(
            {"channel_id": channel_id, "state": statename, "value": default}
        )
        ins_q.execute()
        LOG.debug("    Inserted default value into the database!")
        return default


class Album(object):
    def __init__(self, name, artist, path):
        self.name = name
        self.artist = artist
        self.path = path
        self.added = datetime.now()

    def __repr__(self):
        return "<Album %s name=%s>" % (self.id, repr(self.name))

    @staticmethod
    def by_name(
        name: str, session: Optional[TSession] = None
    ) -> Optional["Album"]:
        session: TSession = session or Session()
        album = session.query(Album).filter_by(name=name).one_or_none()
        return album


class Song(object):
    def __init__(self, localpath: str) -> None:
        self.localpath = localpath
        self.added = datetime.now()

    def __repr__(self):
        return "<Song id=%r artist_id=%r title=%r path=%r>" % (
            self.id,
            self.artist_id,
            self.title,
            self.localpath,
        )

    @staticmethod
    def by_filename(session: TSession, filename: str) -> Optional["Song"]:
        """
        Retrieve a song from the database using the local filename as key
        """
        song = session.query(Song).filter_by(localpath=filename).one_or_none()
        return song

    @staticmethod
    def random(session: TSession) -> Optional["Song"]:
        """
        Retrieve a song from the database using the local filename as key
        """
        query = session.query(Song).order_by(func.rand())
        song = query.first()
        return song

    @staticmethod
    def smart_random(session: TSession, channel_name: str) -> Optional["Song"]:
        """
        Retrieve a song using a smart guess based on play statistics and active
        listeners.
        """
        # TODO: Implement
        from wickedjukebox.core.smartfind import find_song

        song = find_song(session, channel_name)
        return song

    def update_metadata(self) -> None:
        """
        Scans a file on the disk and loads the metadata from that file

        :param localpath: The absolute path to the file
        :param encoding: The file system encoding
        """
        localpath = self.localpath
        LOG.debug("Extracting metadata from %r", localpath)

        audiometa = MetaFactory.create(localpath)
        dirname = path.dirname(localpath)

        artist = Artist.by_name(audiometa["artist"])
        if not artist:
            artist = Artist(audiometa["artist"])
        self.artist = artist

        album = Album.by_name(audiometa["album"])
        if not album:
            album = Album(
                audiometa["album"],
                artist,
                dirname,
            )
        self.album = album

        self.genres = []
        if audiometa["genres"] is not None:
            for genre_name in audiometa["genres"]:
                genre = Genre.by_name(genre_name)
                if not genre:
                    genre = Genre(genre_name)
                self.genres.append(genre)
        self.title = audiometa["title"]
        self.duration = audiometa["duration"]
        self.bitrate = audiometa["bitrate"]
        self.track_no = audiometa["track_no"]

        release_date = audiometa["release_date"]
        if release_date:
            self.year = release_date.year

        self.filesize = stat(localpath).st_size

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

        insq = insert(genreTable).values({"name": genre_name})
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

        insq = insert(artistTable).values({"name": artist_name})
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
            LOG.warning(
                "Unable to determine the album ID without a valid "
                "artist_id and album-name!"
            )

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
                "name": album_name,
                "artist_id": artist_id,
                "path": dirname,
            }
            if self.year:
                data["release_date"] = date(self.year, 1, 1)

            insq = insert(albumTable).values(data)
            result = insq.execute()
            album_id = result.inserted_primary_key[0]

        # if this song's release date is newer than the album's release date,
        # we update the album release date
        if self.year and row:
            if (
                row["release_date"]
                and row["release_date"] < date(self.year, 1, 1)
            ) or (not row["release_date"] and self.year):

                updq = update(albumTable)
                updq = updq.where(albumTable.c.path == dirname)
                updq = updq.values({"release_date": date(self.year, 1, 1)})
                updq.execute()

        return album_id


class QueueItem(object):
    def __init__(self):
        self.added = datetime.now()

    def __repr__(self):
        return "<QueueItem id=%r position=%r song_id=%r>" % (
            self.id,
            self.position,
            self.song_id,
        )


class DynamicPlaylist(object):
    def __repr__(self):
        return "<DynamicPlaylist %s>" % (self.id)


class ChannelStat(object):
    def __init__(self, song_id, channel_id):
        self.song_id = song_id
        self.channel_id = channel_id


class User:
    def __init__(self, username, group, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = username
        self.cookie = ""
        self.password = b64encode(urandom(20)).decode("ascii")
        self.fullname = "default user"
        self.email = ""
        self.proof_of_life = datetime.now()
        self.proof_of_listening = None
        self.IP = ""
        self.credits = 0
        self.group = group
        self.picture = ""
        self.lifetime = 0

    def __repr__(self):
        return "<User %d %r>" % (self.id, self.username)


class Group:
    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title

    def __repr__(self):
        return "<Group %d %r>" % (self.id, self.title)


def setState(statename, value, channel_id=0):
    source = caller_source()
    LOG.warning(
        "DEPRECTAED: Please use State.set!\nSource: %s:%d --> %s",
        source[0],
        source[1],
        source[3],
    )
    return State.set(statename, value, channel_id)


def getState(statename, channel_id=0):
    source = caller_source()
    LOG.warning(
        "DEPRECTAED: Please use State.get!\nSource: %s:%d --> %s",
        source[0],
        source[1],
        source[3],
    )
    return State.get(statename, channel_id)


mapper(
    State,
    stateTable,
    properties={
        # 'channel': relation(Channel)
    },
)
mapper(Genre, genreTable)
mapper(Tag, tagTable)
mapper(ChannelStat, channelSongs)
mapper(DynamicPlaylist, dynamicPLTable)
mapper(QueueItem, queueTable, properties={"song": relation(Song)})
mapper(Channel, channelTable)
mapper(
    Album, albumTable, properties=dict(songs=relation(Song, backref="album"))
)

mapper(
    Artist,
    artistTable,
    properties=dict(
        albums=relation(Album, backref="artist"),
        songs=relation(Song, backref="artist"),
    ),
)
mapper(
    Song,
    songTable,
    properties=dict(
        channelstat=relation(ChannelStat, backref="song"),
        genres=relation(Genre, secondary=song_has_genre, backref="songs"),
        tags=relation(Tag, secondary=song_has_tag, backref="songs"),
    ),
)
mapper(Group, groupsTable)
mapper(
    User,
    usersTable,
    properties={
        "group": relation(Group, backref="users"),
    },
)
