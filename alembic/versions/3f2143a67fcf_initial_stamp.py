"""initial-stamp

Revision ID: 3f2143a67fcf
Revises: None
Create Date: 2014-06-28 18:40:19.905392

"""
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '3f2143a67fcf'
down_revision = None

import sqlalchemy as sa

from alembic import op


def upgrade():

    op.create_table(
        'artist',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('name', sa.Unicode(128)),
        sa.Column('country', sa.Unicode(16)),
        sa.Column('summary', sa.TEXT),
        sa.Column('bio', sa.TEXT),
        sa.Column('website', sa.Unicode(255)),
        sa.Column('wikipage', sa.Unicode(255)),
        sa.Column('lastfm_mbid', sa.Unicode(64)),
        sa.Column('added', sa.DateTime, nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    op.create_table(
        'album',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('artist_id', sa.Integer, nullable=False),
        sa.Column('name', sa.Unicode(128)),
        sa.Column('release_date', sa.Date),
        sa.Column('added', sa.DateTime, nullable=False),
        sa.Column('downloaded', sa.Integer, nullable=False, server_default='0'),
        sa.Column('type', sa.Unicode(32), server_default='album'),
        sa.Column('path', sa.Unicode(255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('path'),
        sa.Index('artistId', 'artist_id'),
        sa.Index('name', 'name'),
        sa.Index('type', 'type'),
        sa.ForeignKeyConstraint(
            ['artist_id'], ['artist.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
    )

    op.create_table(
        'song',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('artist_id', sa.Integer, nullable=False),
        sa.Column('album_id', sa.Integer),
        sa.Column('track_no', sa.Integer),
        sa.Column('title', sa.Unicode(128)),
        sa.Column('duration', sa.DECIMAL(precision=10, scale=4)),
        sa.Column('year', sa.Integer),
        sa.Column('localpath', sa.Unicode(255), nullable=False),
        sa.Column('downloaded', sa.Integer, server_default='0'),
        sa.Column('lastScanned', sa.DateTime),
        sa.Column('bitrate', sa.Integer),
        sa.Column('filesize', sa.Integer),
        sa.Column('checksum', sa.Unicode(14)),
        sa.Column('lyrics', sa.TEXT),
        sa.Column('broken', sa.Boolean, server_default='0'),
        sa.Column('dirty', sa.Boolean, server_default='0'),
        sa.Column('added', sa.DateTime, nullable=False),
        sa.Column('available', sa.Boolean, server_default='1', default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('localpath'),
        sa.Index('artistId', 'artist_id'),
        sa.Index('albumId', 'album_id'),
        sa.Index('broken', 'broken'),
        sa.Index('title', 'title'),
        sa.ForeignKeyConstraint(
            ['artist_id'], ['artist.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['album_id'], ['album.id'], ondelete='SET NULL', onupdate='CASCADE'
        ),
    )

    op.create_table(
        'channel',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('name', sa.Unicode(32), nullable=False),
        sa.Column(
            'public',
            sa.Boolean,
            nullable=False,
            server_default='1',
            default=True,
        ),
        sa.Column('backend', sa.Unicode(64), nullable=False),
        sa.Column('backend_params', sa.TEXT),
        sa.Column('ping', sa.DateTime),
        sa.Column('active', sa.Boolean, nullable=False, server_default='0'),
        sa.Column('status', sa.Integer),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    op.create_table(
        'groups',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('title', sa.Unicode(32), nullable=False),
        sa.Column(
            'admin',
            sa.Boolean,
            nullable=False,
            server_default='0',
            default=False,
        ),
        sa.Column('nocredits', sa.Integer, nullable=False, server_default='0'),
        sa.Column('queue_skip', sa.Integer, nullable=False, server_default='0'),
        sa.Column(
            'queue_remove', sa.Integer, nullable=False, server_default='0'
        ),
        sa.Column('queue_add', sa.Integer, nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('username', sa.Unicode(32), nullable=False),
        sa.Column('cookie', sa.Unicode(32), nullable=False),
        sa.Column('password', sa.Unicode(32), nullable=False),
        sa.Column('fullname', sa.Unicode(64), nullable=False),
        sa.Column('email', sa.Unicode(128), nullable=False),
        sa.Column('credits', sa.Integer, nullable=False),
        sa.Column('group_id', sa.Integer, nullable=False),
        sa.Column('downloads', sa.Integer, nullable=False, server_default='0'),
        sa.Column('votes', sa.Integer, nullable=False, server_default='0'),
        sa.Column('skips', sa.Integer, nullable=False, server_default='0'),
        sa.Column('selects', sa.Integer, nullable=False, server_default='0'),
        sa.Column('added', sa.DateTime, nullable=False),
        sa.Column('proof_of_life', sa.DateTime, nullable=False),
        sa.Column('proof_of_listening', sa.DateTime),
        sa.Column('IP', sa.Unicode(32), nullable=False),
        sa.Column('picture', sa.Unicode(255), nullable=False),
        sa.Column('lifetime', sa.Integer, nullable=False),
        sa.Column('channel_id', sa.Integer, nullable=False, server_default='1'),
        sa.Column('pinnedIp', sa.Unicode(32)),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('cookie'),
        sa.Index('groupId', 'group_id'),
        sa.ForeignKeyConstraint(
            ['group_id'], ['groups.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
    )

    op.create_table(
        'queue',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('song_id', sa.Integer, nullable=False),
        sa.Column('user_id', sa.Integer),
        sa.Column('channel_id', sa.Integer, nullable=False),
        sa.Column('position', sa.Integer, server_default='0'),
        sa.Column('added', sa.DateTime, nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('songId', 'song_id'),
        sa.Index('userId', 'user_id'),
        sa.Index('channelId', 'channel_id'),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['song_id'], ['song.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['channel_id'],
            ['channel.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
    )

    op.create_table(
        'channel_album_data',
        sa.Column('channel_id', sa.Integer, nullable=False),
        sa.Column('album_id', sa.Integer, nullable=False),
        sa.Column('played', sa.Integer, nullable=False, server_default='0'),
        sa.Index('channelId', 'channel_id'),
        sa.Index('albumId', 'album_id'),
        sa.PrimaryKeyConstraint('channel_id', 'album_id'),
        sa.ForeignKeyConstraint(
            ['album_id'], ['album.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['channel_id'],
            ['channel.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
    )

    op.create_table(
        'channel_song_data',
        sa.Column('channel_id', sa.Integer, nullable=False),
        sa.Column('song_id', sa.Integer, nullable=False),
        sa.Column('played', sa.Integer, nullable=False, server_default='0'),
        sa.Column('voted', sa.Integer, nullable=False, server_default='0'),
        sa.Column('skipped', sa.Integer, nullable=False, server_default='0'),
        sa.Column(
            'lastPlayed',
            sa.DateTime,
        ),
        sa.Column('cost', sa.Integer, server_default='5'),
        sa.PrimaryKeyConstraint('channel_id', 'song_id'),
        sa.Index('channelId', 'channel_id'),
        sa.Index('songId', 'song_id'),
        sa.ForeignKeyConstraint(
            ['song_id'], ['song.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['channel_id'],
            ['channel.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
    )

    op.create_table(
        'collection',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('name', sa.Unicode(32), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'collectionhas_song',
        sa.Column('collectionid', sa.Integer, nullable=False),
        sa.Column('song_id', sa.Integer, nullable=False),
        sa.Column('position', sa.Integer),
        sa.Column('last_played', sa.DateTime),
        sa.PrimaryKeyConstraint('collectionid', 'song_id'),
    )

    op.create_table(
        'country',
        sa.Column(
            'country_code', sa.Unicode(16), nullable=False, server_default=''
        ),
        sa.Column(
            'country_name', sa.Unicode(100), nullable=False, server_default=''
        ),
        sa.PrimaryKeyConstraint('country_code'),
    )

    op.create_table(
        'dynamicPlaylist',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('channel_id', sa.Integer),
        sa.Column('group_id', sa.Integer, nullable=False),
        sa.Column(
            'probability',
            sa.Float,
            nullable=False,
            doc='Probability at which a song is picked from the '
            'playlist (0.0-1.0)',
        ),
        sa.Column('label', sa.Unicode(64)),
        sa.Column('query', sa.TEXT),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'events',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('title', sa.Unicode(255), nullable=False),
        sa.Column('startdate', sa.DateTime, nullable=False),
        sa.Column('enddate', sa.DateTime, nullable=False),
        sa.Column('lat', sa.DECIMAL(precision=10, scale=2)),
        sa.Column('lon', sa.DECIMAL(precision=10, scale=2)),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('startdate', 'startdate', 'enddate'),
    )

    op.create_table(
        'genre',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('name', sa.Unicode(128)),
        sa.Column('added', sa.DateTime, nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    op.create_table(
        'history',
        sa.Column('song_id', sa.Integer, nullable=False),
        sa.Column('channel', sa.Integer, nullable=False),
        sa.Column('track', sa.Integer, nullable=False),
        sa.Column('time', sa.Integer, nullable=False),
    )

    op.create_table(
        'lastfm_queue',
        sa.Column('queue_id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('song_id', sa.Integer, nullable=False),
        sa.Column('time_played', sa.DateTime, nullable=False),
        sa.Column('time_started', sa.DateTime, nullable=False),
        sa.PrimaryKeyConstraint('queue_id'),
        sa.Index('songId', 'song_id'),
        sa.ForeignKeyConstraint(
            ['song_id'], ['song.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
    )

    op.create_table(
        'log',
        sa.Column('priority', sa.Unicode(32), nullable=False),
        sa.Column('message', sa.TEXT, nullable=False),
        sa.Column('date', sa.DateTime, nullable=False, default=datetime.now),
    )

    op.create_table(
        'playlist',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('name', sa.Unicode(32), nullable=False),
        sa.Column('probability', sa.Float),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('userId', 'user_id', 'probability'),
    )

    op.create_table(
        'playlist_has_song',
        sa.Column('playlist_id', sa.Integer, nullable=False),
        sa.Column('song_id', sa.Integer, nullable=False),
        sa.PrimaryKeyConstraint('playlist_id', 'song_id'),
    )

    op.create_table(
        'render_presets',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('category', sa.Unicode(64), nullable=False),
        sa.Column('preset', sa.Unicode(64), nullable=False),
        sa.Column('hmax', sa.Integer, nullable=False),
        sa.Column('wmax', sa.Integer, nullable=False),
        sa.Column('placeholder', sa.Unicode(64)),
        sa.Column(
            'noproportion', sa.Boolean, nullable=False, server_default='0'
        ),
        sa.Column(
            'force_mime',
            sa.Enum('image/jpeg', 'image/gif', 'image/png'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('category', 'category', 'preset'),
    )

    op.create_table(
        'setting',
        sa.Column('var', sa.Unicode(32), nullable=False),
        sa.Column('value', sa.TEXT),
        sa.Column('channel_id', sa.Integer, nullable=False, server_default='0'),
        sa.Column('user_id', sa.Integer, nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('var', 'channel_id', 'user_id'),
        sa.Index('channelId', 'channel_id'),
        sa.Index('userId', 'user_id'),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['channel_id'],
            ['channel.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
    )

    op.create_table(
        'setting_text',
        sa.Column('var', sa.Unicode(32), nullable=False),
        sa.Column('text_en', sa.TEXT, nullable=False),
        sa.PrimaryKeyConstraint('var'),
    )

    op.create_table(
        'shoutbox',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('message', sa.Unicode(255), nullable=False),
        sa.Column('added', sa.DateTime, nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('when', 'added'),
        sa.Index('userId', 'user_id'),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
    )

    op.create_table(
        'song_has_genre',
        sa.Column('song_id', sa.Integer, nullable=False),
        sa.Column('genre_id', sa.Integer, nullable=False),
        sa.PrimaryKeyConstraint('song_id', 'genre_id'),
        sa.Index('songId', 'song_id'),
        sa.Index('genreId', 'genre_id'),
        sa.ForeignKeyConstraint(
            ['genre_id'], ['genre.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['song_id'], ['song.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
    )

    op.create_table(
        'song_has_tag',
        sa.Column('song_id', sa.Integer, nullable=False),
        sa.Column('tag', sa.Unicode(32), nullable=False),
        sa.PrimaryKeyConstraint('song_id', 'tag'),
    )

    op.create_table(
        'state',
        sa.Column('channel_id', sa.Integer, nullable=False),
        sa.Column('state', sa.Unicode(64), nullable=False),
        sa.Column(
            'value',
            sa.Unicode(255),
        ),
        sa.PrimaryKeyConstraint('channel_id', 'state'),
    )

    op.create_table(
        'tag',
        sa.Column('label', sa.Unicode(32), nullable=False),
        sa.Column(
            'inserted', sa.DateTime, nullable=False, default=datetime.now
        ),
        sa.Column('modified', sa.DateTime, nullable=False),
        sa.PrimaryKeyConstraint('label'),
    )

    op.create_table(
        'user_album_stats',
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('album_id', sa.Integer, nullable=False),
        sa.Column('when', sa.DateTime, nullable=False),
        sa.Index('userId', 'user_id'),
        sa.Index('albumId', 'album_id'),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['album_id'], ['album.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
    )

    op.create_table(
        'user_song_standing',
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('song_id', sa.Integer, nullable=False),
        sa.Column('standing', sa.Enum('love', 'hate'), nullable=False),
        sa.Column('inserted', sa.DateTime, default=datetime.now),
        sa.PrimaryKeyConstraint('user_id', 'song_id'),
        sa.Index('userId', 'user_id'),
        sa.Index('songId', 'song_id'),
        sa.ForeignKeyConstraint(
            ['song_id'], ['song.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
    )

    op.create_table(
        'user_song_stats',
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('song_id', sa.Integer, nullable=False),
        sa.Column('when', sa.DateTime, nullable=False),
        sa.PrimaryKeyConstraint('user_id', 'song_id', 'when'),
        sa.Index('userId', 'user_id'),
        sa.Index('songId', 'song_id'),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['song_id'], ['song.id'], ondelete='CASCADE', onupdate='CASCADE'
        ),
    )


def downgrade():
    pass
