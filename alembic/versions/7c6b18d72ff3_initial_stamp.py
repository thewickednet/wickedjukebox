# type: ignore
# pylint: skip-file
"""
initial-stamp

Revision ID: 7c6b18d72ff3
Revises: None
Create Date: 2021-12-31 12:14:53.609181

"""

# revision identifiers, used by Alembic.
revision = "7c6b18d72ff3"
down_revision = None

import enum
from datetime import datetime
from textwrap import dedent

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import MetaData
from sqlalchemy.sql.schema import ForeignKeyConstraint

from alembic import op


class StandingEnum(enum.Enum):
    LOVE = "love"
    HATE = "hate"


class ImageEnum(enum.Enum):
    JPEG = "image/jpeg"
    GIF = "image/gif"
    PNG = "image/png"


def define_tables(Base):
    class User(Base):
        __tablename__ = "users"
        __table_args__ = (
            Index("group_id", "group_id", unique=False),
            Index("username", "username", unique=True),
            Index("cookie", "cookie", unique=True),
            Index("django_user_id_idx", "django_user_id", unique=True),
            ForeignKeyConstraint(
                ["group_id"],
                ["groups.id"],
                name="users_ibfk_1",
                ondelete="CASCADE",
                onupdate="CASCADE",
            ),
        )
        id = Column(Integer, primary_key=True)
        username = Column(String(32), nullable=False)
        cookie = Column(String(32), nullable=False)
        password = Column(String(32), nullable=False)
        fullname = Column(String(64), nullable=False)
        email = Column(String(128), nullable=False)
        credits = Column(Integer, nullable=False)
        group_id = Column(Integer, nullable=False)
        downloads = Column(Integer, nullable=False, server_default=text("0"))
        votes = Column(Integer, nullable=False, server_default=text("0"))
        skips = Column(Integer, nullable=False, server_default=text("0"))
        selects = Column(Integer, nullable=False, server_default=text("0"))
        added = Column(DateTime, nullable=False, default=datetime.now)
        proof_of_life = Column(DateTime, nullable=False)
        proof_of_listening = Column(DateTime)
        IP = Column(String(32), nullable=False)
        picture = Column(String(255), nullable=False)
        lifetime = Column(BigInteger, nullable=False)
        channel_id = Column(Integer, nullable=False, server_default=text("1"))
        pinnedIp = Column(String(32))
        django_user_id = Column(Integer)

        group = relationship("Group", backref="users")

    class Group(Base):
        __tablename__ = "groups"

        id = Column(Integer, primary_key=True)
        title = Column(String(32), nullable=False)
        admin = Column(Integer, nullable=False, server_default=text("0"))
        nocredits = Column(Integer, nullable=False, server_default=text("0"))
        queue_skip = Column(Integer, nullable=False, server_default=text("0"))
        queue_remove = Column(Integer, nullable=False, server_default=text("0"))
        queue_add = Column(Integer, nullable=False, server_default=text("0"))

    class AuthGroup(Base):
        __tablename__ = "auth_group"

        id = Column(Integer, primary_key=True)
        name = Column(String(150), nullable=False, unique=True)

    class AuthUser(Base):
        __tablename__ = "auth_user"

        id = Column(Integer, primary_key=True)
        password = Column(String(128), nullable=False)
        last_login = Column(DateTime(timezone=True))
        is_superuser = Column(Boolean, nullable=False)
        username = Column(String(150), nullable=False, unique=True)
        first_name = Column(String(150), nullable=False)
        last_name = Column(String(150), nullable=False)
        email = Column(String(254), nullable=False)
        is_staff = Column(Boolean, nullable=False)
        is_active = Column(Boolean, nullable=False)
        date_joined = Column(DateTime(timezone=True), nullable=False)

    class AuthPermission(Base):
        __tablename__ = "auth_permission"
        __table_args__ = (
            Index(
                "auth_permission_content_type_id_codename_01ab375a_uniq",
                "content_type_id",
                "codename",
                unique=True,
            ),
        )

        id = Column(Integer, primary_key=True)
        name = Column(String(255), nullable=False)
        content_type_id = Column(
            ForeignKey("django_content_type.id"), nullable=False
        )
        codename = Column(String(100), nullable=False)

        content_type = relationship("DjangoContentType")

    class AuthUserGroup(Base):
        __tablename__ = "auth_user_groups"
        __table_args__ = (
            Index(
                "auth_user_groups_group_id_97559544_fk_auth_group_id",
                "group_id",
                unique=False,
            ),
            Index(
                "auth_user_groups_user_id_group_id_94350c0c_uniq",
                "user_id",
                "group_id",
                unique=True,
            ),
        )

        id = Column(Integer, primary_key=True)
        user_id = Column(ForeignKey("auth_user.id"), nullable=False)
        group_id = Column(ForeignKey("auth_group.id"), nullable=False)

        group = relationship("AuthGroup")
        user = relationship("AuthUser")

    class AuthGroupPermission(Base):
        __tablename__ = "auth_group_permissions"
        __table_args__ = (
            Index(
                "auth_group_permissions_group_id_permission_id_0cd325b0_uniq",
                "group_id",
                "permission_id",
                unique=True,
            ),
        )

        id = Column(Integer, primary_key=True)
        group_id = Column(ForeignKey("auth_group.id"), nullable=False)
        permission_id = Column(ForeignKey("auth_permission.id"), nullable=False)

        group = relationship("AuthGroup")
        permission = relationship("AuthPermission")

    class AuthUserUserPermission(Base):
        __tablename__ = "auth_user_user_permissions"
        __table_args__ = (
            Index(
                "auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm",
                "permission_id",
                unique=False,
            ),
            Index(
                "auth_user_user_permissions_user_id_permission_id_14a6b632_uniq",
                "user_id",
                "permission_id",
                unique=True,
            ),
        )

        id = Column(Integer, primary_key=True)
        user_id = Column(ForeignKey("auth_user.id"), nullable=False)
        permission_id = Column(ForeignKey("auth_permission.id"), nullable=False)

        permission = relationship("AuthPermission")
        user = relationship("AuthUser")

    class Event(Base):
        __tablename__ = "events"
        __table_args__ = (Index("startdate", "startdate", "enddate"),)

        id = Column(Integer, primary_key=True)
        title = Column(String(255), nullable=False)
        startdate = Column(DateTime, nullable=False)
        enddate = Column(DateTime, nullable=False)
        lat = Column(Float)
        lon = Column(Float)

    class LastfmQueue(Base):
        __tablename__ = "lastfm_queue"
        __table_args__ = (
            Index("song_id", "song_id", unique=False),
            ForeignKeyConstraint(
                ["song_id"],
                ["song.id"],
                name="lastfm_queue_ibfk_2",
                onupdate="CASCADE",
                ondelete="CASCADE",
            ),
        )

        queue_id = Column(Integer, primary_key=True)
        song_id = Column(Integer, nullable=False)
        time_played = Column(DateTime, nullable=False)
        time_started = Column(DateTime, nullable=False)

        song = relationship("Song")

    class Genre(Base):
        __tablename__ = "genre"

        id = Column(Integer, primary_key=True)
        name = Column(String(128), unique=True)
        added = Column(DateTime, nullable=False)

    class Tag(Base):
        __tablename__ = "tag"
        id = Column(Integer, primary_key=True)
        label = Column(String(32), nullable=False, unique=True)
        inserted = Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("current_timestamp()"),
        )
        modified = Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("'0000-00-00 00:00:00'"),
        )

    class Artist(Base):
        __tablename__ = "artist"

        id = Column(Integer, primary_key=True)
        name = Column(String(128), unique=True)
        country = Column(String(16))
        summary = Column(Text())
        bio = Column(Text())
        website = Column(String(255))
        wikipage = Column(String(255))
        lastfm_mbid = Column(String(64))
        lastfm_url = Column(String(255))
        added = Column(DateTime)
        photo = Column(String(255))

    class Album(Base):
        __tablename__ = "album"
        __table_args__ = (
            Index("artist_id", "artist_id", unique=False),
            Index("name", "name", unique=False),
            Index("type", "type", unique=False),
        )
        id = Column(Integer, primary_key=True)
        artist_id = Column(
            Integer,
            ForeignKey("artist.id", ondelete="CASCADE", onupdate="CASCADE"),
            nullable=False,
        )
        name = Column(String(128), index=True)
        release_date = Column(Date)
        added = Column(DateTime, nullable=False)
        downloaded = Column(Integer, nullable=False, server_default=text("0"))
        type = Column(String(32), server_default=text("'album'"))
        path = Column(String(255), nullable=False, unique=True)
        coverart = Column(String(255))
        lastfm_mbid = Column(String(255))
        lastfm_url = Column(String(255))

        artist = relationship("Artist", backref="albums")

    class Song(Base):
        __tablename__ = "song"
        __table_args__ = (
            Index("album_id", "album_id", unique=False),
            Index("artist_id", "artist_id", unique=False),
            Index("broken", "broken", unique=False),
            Index("title", "title", unique=False),
            ForeignKeyConstraint(
                ["artist_id"],
                ["artist.id"],
                name="song_ibfk_1",
                ondelete="CASCADE",
                onupdate="CASCADE",
            ),
            ForeignKeyConstraint(
                ["album_id"],
                ["album.id"],
                name="song_ibfk_2",
                ondelete="SET NULL",
                onupdate="CASCADE",
            ),
        )

        id = Column(Integer, primary_key=True)
        artist_id = Column(Integer, nullable=False)
        album_id = Column(Integer)
        track_no = Column(Integer)
        title = Column(String(128))
        duration = Column(Float(asdecimal=True))
        year = Column(Integer)
        localpath = Column(String(255), nullable=False, unique=True)
        downloaded = Column(Integer, server_default=text("0"))
        lastScanned = Column(DateTime)
        bitrate = Column(Integer)
        filesize = Column(Integer)
        checksum = Column(String(14))
        lyrics = Column(Text())
        broken = Column(Boolean, server_default=text("0"))
        dirty = Column(Boolean, server_default=text("0"))
        added = Column(DateTime, nullable=False)
        available = Column(Boolean, server_default=text("1"))
        coverart = Column(String(255))
        lastfm_mbid = Column(String(255))
        lastfm_url = Column(String(255))

        album = relationship("Album")
        artist = relationship("Artist")
        tags = relationship(Tag, secondary="song_has_tag", backref="songs")

    class Collection(Base):
        __tablename__ = "collection"

        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, nullable=False)
        name = Column(String(32), nullable=False)
        is_active = Column(Boolean, nullable=False, server_default=text("0"))

    class CollectionhasSong(Base):
        __tablename__ = "collection_has_song"
        __table_args__ = (
            Index("collection_id", "collection_id", "song_id", unique=True),
        )

        id = Column(Integer, primary_key=True)
        collection_id = Column(Integer, nullable=False)
        song_id = Column(Integer, nullable=False)
        position = Column(Integer)
        last_played = Column(DateTime)

    class Country(Base):
        __tablename__ = "country"

        country_code = Column(
            String(16),
            primary_key=True,
            server_default=text("''"),
        )
        country_name = Column(
            String(100),
            nullable=False,
            server_default=text("''"),
        )

    class Playlist(Base):
        __tablename__ = "playlist"
        __table_args__ = (Index("user_id", "user_id", "probability"),)

        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, nullable=False)
        name = Column(String(32), nullable=False)
        probability = Column(Float)

    class PlaylistHasSong(Base):
        __tablename__ = "playlist_has_song"

        playlist_id = Column(Integer, primary_key=True, nullable=False)
        song_id = Column(Integer, primary_key=True, nullable=False)

    class SongHasTag(Base):
        __tablename__ = "song_has_tag"
        __table_args__ = (Index("song_id", "song_id", "tag_id", unique=True),)

        id = Column(Integer, primary_key=True)
        song_id = Column(Integer, nullable=False)
        tag_id = Column(Integer, nullable=False)

    class UserSongStanding(Base):
        __tablename__ = "user_song_standing"
        __table_args__ = (
            Index("user_song_id", "user_id", "song_id", unique=True),
        )

        id = Column(Integer, primary_key=True)
        user_id = Column(
            Integer,
            ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
            nullable=False,
        )
        song_id = Column(
            Integer,
            ForeignKey("song.id", ondelete="CASCADE", onupdate="CASCADE"),
            nullable=False,
        )
        standing = Column(Enum(StandingEnum), nullable=False)
        inserted = Column(
            DateTime(timezone=True), server_default=text("current_timestamp()")
        )

    class SongHasGenre(Base):
        __tablename__ = "song_has_genre"
        __table_args__ = (
            Index("song_id_2", "song_id", "genre_id", unique=True),
            Index("song_id", "genre_id", unique=False),
            Index("genre_id", "song_id", unique=False),
            ForeignKeyConstraint(
                ["song_id"],
                ["song.id"],
                name="song_has_genre_ibfk_2",
                ondelete="CASCADE",
                onupdate="CASCADE",
            ),
            ForeignKeyConstraint(
                ["genre_id"],
                ["genre.id"],
                name="song_has_genre_ibfk_1",
                ondelete="CASCADE",
                onupdate="CASCADE",
            ),
        )

        id = Column(Integer, primary_key=True)
        song_id = Column(
            Integer,
            nullable=False,
        )
        genre_id = Column(
            Integer,
            nullable=False,
        )

        genre = relationship("Genre")
        song = relationship("Song")

    t_log = Table(
        "log",
        Base.metadata,
        Column("priority", String(32), nullable=False),
        Column("message", Text, nullable=False),
        Column(
            "date",
            DateTime(timezone=True),
            nullable=False,
            server_default=text(
                "current_timestamp() ON UPDATE current_timestamp()"
            ),
        ),
    )

    class Channel(Base):
        __tablename__ = "channel"
        id = Column(Integer, primary_key=True)
        name = Column(String(32), nullable=False, unique=True)
        public = Column(Boolean, nullable=False, server_default=text("1"))
        backend = Column(String(64), nullable=False)
        backend_params = Column(Text())
        ping = Column(DateTime)
        active = Column(Boolean, nullable=False, server_default=text("0"))
        status = Column(Integer)

    class State(Base):
        __tablename__ = "state"
        __table_args__ = (
            Index("channel_id", "channel_id", "state", unique=True),
        )

        id = Column(Integer, primary_key=True)
        channel_id = Column(Integer, nullable=False)
        state = Column(String(64), nullable=False)
        value = Column(String(255))

    class QueueItem(Base):
        __tablename__ = "queue"
        __table_args__ = (
            Index("channel_id", "channel_id", unique=False),
            Index("position", "position", unique=False),
            Index("song_id", "song_id", unique=False),
            Index("user_id", "user_id", unique=False),
            ForeignKeyConstraint(
                ["song_id"],
                ["song.id"],
                name="queue_ibfk_2",
                ondelete="CASCADE",
                onupdate="CASCADE",
            ),
            ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                name="queue_ibfk_1",
                ondelete="CASCADE",
                onupdate="CASCADE",
            ),
            ForeignKeyConstraint(
                ["channel_id"],
                ["channel.id"],
                name="queue_ibfk_3",
                ondelete="CASCADE",
                onupdate="CASCADE",
            ),
        )
        id = Column(Integer, primary_key=True)
        song_id = Column(Integer, nullable=False)
        user_id = Column(Integer)
        channel_id = Column(Integer, nullable=False)
        position = Column(Integer, server_default=text("0"))
        added = Column(DateTime, nullable=False)

        channel = relationship("Channel")
        song = relationship("Song")
        user = relationship("User")

    class DynamicPlaylist(Base):
        __tablename__ = "dynamicPlaylist"
        id = Column(Integer, primary_key=True)
        channel_id = Column(Integer)
        group_id = Column(Integer, nullable=False)
        probability = Column(
            Float,
            nullable=False,
            comment="Probability at which a song is picked from the playlisy (0.0-1.0)",
        )
        label = Column(String(64))
        query = Column(Text())

    class RandomSongsToUse(Base):
        __tablename__ = "randomSongsToUse"
        __table_args__ = (Index("used", "used", unique=False),)

        id = Column(Integer, primary_key=True)
        used = Column(Boolean, nullable=False, server_default=text("0"))
        in_string = Column(String(255), nullable=False)

    class Setting(Base):
        __tablename__ = "setting"
        __table_args__ = (
            Index("var", "var", unique=False),
            Index("channel_id", "channel_id", unique=False),
            Index("user_id", "user_id", unique=False),
            Index("var_2", "var", "channel_id", "user_id", unique=True),
            ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                name="setting_ibfk_1",
                onupdate="CASCADE",
                ondelete="CASCADE",
            ),
            ForeignKeyConstraint(
                ["channel_id"],
                ["channel.id"],
                name="setting_ibfk_2",
                onupdate="CASCADE",
                ondelete="CASCADE",
            ),
        )
        id = Column(Integer, nullable=False, primary_key=True)
        var = Column(String(32), nullable=False)
        value = Column(String(255))
        channel_id = Column(
            Integer,
            nullable=False,
            server_default=text("0"),
        )
        user_id = Column(
            Integer,
            nullable=False,
            server_default=text("0"),
        )

    class SettingText(Base):
        __tablename__ = "setting_text"

        var = Column(String(32), nullable=False, primary_key=True)
        text_en = Column(Text, nullable=False)

    t_user_album_stats = Table(
        "user_album_stats",
        Base.metadata,
        Column("user_id", Integer, nullable=False),
        Column("album_id", Integer, nullable=False),
        Column("when", DateTime, nullable=False),
        Index("album_id", "album_id", unique=False),
        Index("user_id", "user_id", unique=False),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="user_album_stats_ibfk_1",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        ForeignKeyConstraint(
            ["album_id"],
            ["album.id"],
            name="user_album_stats_ibfk_2",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    class UserSongStat(Base):
        __tablename__ = "user_song_stats"
        __table_args__ = (
            Index("song_id", "song_id", unique=False),
            Index("user_id", "user_id", unique=False),
            ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                name="user_song_stats_ibfk_1",
                ondelete="CASCADE",
                onupdate="CASCADE",
            ),
            ForeignKeyConstraint(
                ["song_id"],
                ["song.id"],
                name="user_song_stats_ibfk_2",
                ondelete="CASCADE",
                onupdate="CASCADE",
            ),
        )

        user_id = Column(
            Integer,
            primary_key=True,
            nullable=False,
        )
        song_id = Column(
            Integer,
            primary_key=True,
            nullable=False,
        )
        when = Column(DateTime, primary_key=True, nullable=False)

        song = relationship("Song")
        user = relationship("User")

    class ChannelAlbumDatum(Base):
        __tablename__ = "channel_album_data"
        __table_args__ = (
            Index("channel_id_2", "channel_id", "album_id", unique=True),
        )

        id = Column(Integer, primary_key=True)
        channel_id = Column(Integer, nullable=False)
        album_id = Column(Integer, nullable=False)
        played = Column(Integer, nullable=False, server_default=text("0"))

    class ChannelStat(Base):
        __tablename__ = "channel_song_data"
        __table_args__ = (
            Index("channel_id_2", "channel_id", "song_id", unique=True),
            Index("song_id", "song_id", unique=False),
            Index("channel_id", "channel_id", unique=False),
        )

        id = Column(Integer, primary_key=True)
        channel_id = Column(
            ForeignKey("channel.id", ondelete="CASCADE", onupdate="CASCADE"),
            nullable=False,
        )
        song_id = Column(
            ForeignKey("song.id", ondelete="CASCADE", onupdate="CASCADE"),
            nullable=False,
        )
        played = Column(Integer, nullable=False, server_default=text("0"))
        voted = Column(Integer, nullable=False, server_default=text("0"))
        skipped = Column(Integer, nullable=False, server_default=text("0"))
        lastPlayed = Column(DateTime)
        cost = Column(Integer, server_default=text("5"))

        channel = relationship("Channel")
        song = relationship("Song")

    class DjangoCeleryResultsChordcounter(Base):
        __tablename__ = "django_celery_results_chordcounter"

        id = Column(Integer, primary_key=True)
        group_id = Column(String(255), nullable=False, unique=True)
        sub_tasks = Column(Text, nullable=False)
        count = Column(Integer, nullable=False)

    class DjangoCeleryResultsGroupresult(Base):
        __tablename__ = "django_celery_results_groupresult"
        __table_args__ = (
            Index(
                "django_cele_date_cr_bd6c1d_idx",
                "date_created",
                unique=False,
            ),
            Index(
                "django_cele_date_do_caae0e_idx",
                "date_done",
                unique=False,
            ),
        )

        id = Column(Integer, primary_key=True)
        group_id = Column(String(255), nullable=False, unique=True)
        date_created = Column(DateTime(timezone=True), nullable=False)
        date_done = Column(DateTime(timezone=True), nullable=False)
        content_type = Column(String(128), nullable=False)
        content_encoding = Column(String(64), nullable=False)
        result = Column(Text)

    class DjangoCeleryResultsTaskresult(Base):
        __tablename__ = "django_celery_results_taskresult"
        __table_args__ = (
            Index(
                "django_cele_task_na_08aec9_idx",
                "task_name",
                unique=False,
            ),
            Index(
                "django_cele_status_9b6201_idx",
                "status",
                unique=False,
            ),
            Index(
                "django_cele_worker_d54dd8_idx",
                "worker",
                unique=False,
            ),
            Index(
                "django_cele_date_cr_f04a50_idx",
                "date_created",
                unique=False,
            ),
            Index(
                "django_cele_date_do_f59aad_idx",
                "date_done",
                unique=False,
            ),
        )

        id = Column(Integer, primary_key=True)
        task_id = Column(String(255), nullable=False, unique=True)
        status = Column(String(50), nullable=False)
        content_type = Column(String(128), nullable=False)
        content_encoding = Column(String(64), nullable=False)
        result = Column(Text)
        date_done = Column(DateTime(timezone=True), nullable=False)
        traceback = Column(Text)
        meta = Column(Text)
        task_args = Column(Text)
        task_kwargs = Column(Text)
        task_name = Column(String(255))
        worker = Column(String(100))
        date_created = Column(DateTime(timezone=True), nullable=False)

    class DjangoContentType(Base):
        __tablename__ = "django_content_type"
        __table_args__ = (
            Index(
                "django_content_type_app_label_model_76bd3d3b_uniq",
                "app_label",
                "model",
                unique=True,
            ),
        )

        id = Column(Integer, primary_key=True)
        app_label = Column(String(100), nullable=False)
        model = Column(String(100), nullable=False)

    class DjangoMigration(Base):
        __tablename__ = "django_migrations"

        id = Column(Integer, primary_key=True)
        app = Column(String(255), nullable=False)
        name = Column(String(255), nullable=False)
        applied = Column(DateTime(timezone=True), nullable=False)

    class DjangoSession(Base):
        __tablename__ = "django_session"
        __table_args__ = (
            Index(
                "django_session_expire_date_a5c62663",
                "expire_date",
                unique=False,
            ),
        )

        session_key = Column(String(40), primary_key=True)
        session_data = Column(Text, nullable=False)
        expire_date = Column(DateTime(timezone=True), nullable=False)

    class DjangoAdminLog(Base):
        __tablename__ = "django_admin_log"
        __table_args__ = (
            Index(
                "django_admin_log_content_type_id_c4bce8eb_fk_django_co",
                "content_type_id",
                unique=False,
            ),
            Index(
                "django_admin_log_user_id_c564eba6_fk_auth_user_id",
                "user_id",
                unique=False,
            ),
        )

        id = Column(Integer, primary_key=True)
        action_time = Column(DateTime(timezone=True), nullable=False)
        object_id = Column(Text)
        object_repr = Column(String(200), nullable=False)
        action_flag = Column(Integer, nullable=False)
        change_message = Column(Text, nullable=False)
        content_type_id = Column(ForeignKey("django_content_type.id"))
        user_id = Column(ForeignKey("auth_user.id"), nullable=False)

        content_type = relationship("DjangoContentType")
        user = relationship("AuthUser")

    class RestFrameworkTrackingApirequestlog(Base):
        __tablename__ = "rest_framework_tracking_apirequestlog"
        __table_args__ = (
            Index(
                "rest_framework_tracking_apirequestlog_path_fe81f91b",
                "path",
                unique=False,
            ),
            Index(
                "rest_framework_tracking_apirequestlog_requested_at_b6f1c2f2",
                "requested_at",
                unique=False,
            ),
            Index(
                "rest_framework_tracking_apirequestlog_status_code_3c9e2003",
                "status_code",
                unique=False,
            ),
            Index(
                "rest_framework_track_user_id_671b70b7_fk_auth_user",
                "user_id",
                unique=False,
            ),
            Index(
                "rest_framework_tracking_apirequestlog_view_5bd1e407",
                "view",
                unique=False,
            ),
            Index(
                "rest_framework_tracking_apirequestlog_view_method_dd790881",
                "view_method",
                unique=False,
            ),
            ForeignKeyConstraint(
                ["user_id"],
                ["auth_user.id"],
                name="rest_framework_track_user_id_671b70b7_fk_auth_user",
            ),
        )

        id = Column(Integer, primary_key=True)
        requested_at = Column(DateTime(timezone=True), nullable=False)
        response_ms = Column(Integer, nullable=False)
        path = Column(String(200), nullable=False)
        remote_addr = Column(String(39), nullable=False)
        host = Column(String(200), nullable=False)
        method = Column(String(10), nullable=False)
        query_params = Column(Text)
        data = Column(Text)
        response = Column(Text)
        status_code = Column(Integer)
        user_id = Column(Integer)
        view = Column(String(200))
        view_method = Column(String(200))
        errors = Column(Text)
        username_persistent = Column(String(200))

        user = relationship("AuthUser")

    class RenderPreset(Base):
        __tablename__ = "render_presets"
        __table_args__ = (Index("category", "category", "preset"),)

        id = Column(Integer, primary_key=True)
        category = Column(String(64), nullable=False)
        preset = Column(String(64), nullable=False)
        description = Column(String(255))
        hmax = Column(Integer, nullable=False)
        wmax = Column(Integer, nullable=False)
        placeholder = Column(String(64))
        noproportion = Column(Boolean)
        force_mime = Column(Enum(ImageEnum))
        crop = Column(
            String(8),
            nullable=False,
            server_default=text("'center'"),
        )
        placeholder_image = Column(String(255))

    class ThumbnailKvstore(Base):
        __tablename__ = "thumbnail_kvstore"

        key = Column(String(200), primary_key=True)
        value = Column(Text, nullable=False)

    class Shoutbox(Base):
        __tablename__ = "shoutbox"
        __table_args__ = (
            Index("when", "added", unique=False),
            Index("user_id", "user_id", unique=False),
            ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                name="shoutbox_ibfk_1",
                onupdate="CASCADE",
                ondelete="CASCADE",
            ),
        )

        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, nullable=False)
        message = Column(String(255), nullable=False)
        added = Column(DateTime(timezone=True), nullable=False)

        user = relationship("User")


def upgrade():
    Base = declarative_base()
    metadata = MetaData(bind=op.get_bind())
    Base.metadata = metadata
    define_tables(Base)
    metadata.create_all()

    op.execute(
        dedent(
            """\
        CREATE VIEW `history` AS
        select
            `s`.`id` AS `song_id`,
            `rel`.`channel_id` AS `channel`,
            concat(`a`.`name`,_utf8' - ',`s`.`title`) AS `track`,
            `rel`.`lastPlayed` AS `time`
        from (
            (
                `channel_song_data` `rel`
                join `song` `s` on (`s`.`id` = `rel`.`song_id`)
            )
            join `artist` `a` on (`a`.`id` = `s`.`artist_id`)
        )
        order by `rel`.`lastPlayed` desc ;
        """
        )
    )


def downgrade():
    pass
