# type: ignore
# pylint: skip-file
"""djukebox field parity

Bring the alembic-managed schema in line with the SQLAlchemy models after they
were updated to match djukebox's "music" app (the owner of the shared schema):
add the new library/playback columns, rename ``lastfm_mbid`` -> ``mbid`` (UUID,
char(32)) on artist/album/song, and widen ``song.checksum``/``song.title``.

Revision ID: b3d9f1a2c4e6
Revises: 318551dda932
Create Date: 2026-06-28
"""

import sqlalchemy as sa

from alembic import op

revision = "b3d9f1a2c4e6"
down_revision = "318551dda932"


def upgrade():
    # --- genre ---
    op.add_column("genre", sa.Column("slug", sa.String(50), nullable=True))
    op.create_unique_constraint("uq_genre_slug", "genre", ["slug"])

    # --- artist ---
    op.add_column("artist", sa.Column("slug", sa.String(50), nullable=True))
    op.add_column("artist", sa.Column("mbid", sa.String(32), nullable=True))
    op.add_column(
        "artist", sa.Column("founded_year", sa.SmallInteger(), nullable=True)
    )
    op.drop_column("artist", "lastfm_mbid")
    op.create_unique_constraint("uq_artist_slug", "artist", ["slug"])

    # --- album ---
    op.add_column("album", sa.Column("slug", sa.String(50), nullable=True))
    op.add_column(
        "album",
        sa.Column(
            "disc_no",
            sa.SmallInteger(),
            nullable=False,
            server_default="1",
        ),
    )
    op.add_column("album", sa.Column("mbid", sa.String(32), nullable=True))
    op.drop_column("album", "lastfm_mbid")
    op.create_unique_constraint("uq_album_slug", "album", ["slug"])

    # --- song ---
    op.add_column("song", sa.Column("slug", sa.String(50), nullable=True))
    op.add_column("song", sa.Column("intro_id", sa.Integer(), nullable=True))
    op.add_column(
        "song",
        sa.Column(
            "disc_no", sa.SmallInteger(), nullable=False, server_default="1"
        ),
    )
    op.add_column(
        "song",
        sa.Column(
            "lyrics_synced", sa.Text(), nullable=False, server_default=""
        ),
    )
    op.add_column("song", sa.Column("waveform", sa.Text(), nullable=True))
    op.add_column("song", sa.Column("bpm", sa.SmallInteger(), nullable=True))
    op.add_column("song", sa.Column("musical_key", sa.String(8), nullable=True))
    op.add_column("song", sa.Column("loudness", sa.Float(), nullable=True))
    op.add_column("song", sa.Column("true_peak", sa.Float(), nullable=True))
    op.add_column("song", sa.Column("crest_factor", sa.Float(), nullable=True))
    op.add_column(
        "song", sa.Column("replaygain_written", sa.DateTime(), nullable=True)
    )
    op.add_column("song", sa.Column("asin", sa.String(32), nullable=True))
    op.add_column("song", sa.Column("acoustid_id", sa.String(32), nullable=True))
    op.add_column(
        "song",
        sa.Column(
            "acoustid_fingerprint",
            sa.Text(),
            nullable=False,
            server_default="",
        ),
    )
    op.add_column("song", sa.Column("mbid", sa.String(32), nullable=True))
    op.drop_column("song", "lastfm_mbid")
    op.alter_column(
        "song",
        "checksum",
        existing_type=sa.String(14),
        type_=sa.String(64),
        existing_nullable=True,
    )
    op.alter_column(
        "song",
        "title",
        existing_type=sa.String(128),
        type_=sa.String(255),
        existing_nullable=True,
    )
    op.create_unique_constraint("uq_song_slug", "song", ["slug"])
    op.create_unique_constraint("uq_song_intro_id", "song", ["intro_id"])

    # --- playlist ---
    op.add_column("playlist", sa.Column("slug", sa.String(50), nullable=True))
    op.add_column(
        "playlist",
        sa.Column(
            "public", sa.Boolean(), nullable=False, server_default=sa.text("0")
        ),
    )
    op.create_unique_constraint("uq_playlist_slug", "playlist", ["slug"])

    # --- playlist_has_song ---
    op.add_column(
        "playlist_has_song", sa.Column("position", sa.Integer(), nullable=True)
    )
    op.add_column(
        "playlist_has_song", sa.Column("added", sa.DateTime(), nullable=True)
    )

    # --- channel ---
    op.add_column("channel", sa.Column("owner_id", sa.Integer(), nullable=True))

    # --- events ---
    op.add_column("events", sa.Column("slug", sa.String(50), nullable=True))
    op.add_column("events", sa.Column("photo", sa.String(100), nullable=True))
    op.create_unique_constraint("uq_events_slug", "events", ["slug"])


def downgrade():
    op.drop_constraint("uq_events_slug", "events", type_="unique")
    op.drop_column("events", "photo")
    op.drop_column("events", "slug")

    op.drop_column("channel", "owner_id")

    op.drop_column("playlist_has_song", "added")
    op.drop_column("playlist_has_song", "position")

    op.drop_constraint("uq_playlist_slug", "playlist", type_="unique")
    op.drop_column("playlist", "public")
    op.drop_column("playlist", "slug")

    op.drop_constraint("uq_song_intro_id", "song", type_="unique")
    op.drop_constraint("uq_song_slug", "song", type_="unique")
    op.alter_column(
        "song",
        "title",
        existing_type=sa.String(255),
        type_=sa.String(128),
        existing_nullable=True,
    )
    op.alter_column(
        "song",
        "checksum",
        existing_type=sa.String(64),
        type_=sa.String(14),
        existing_nullable=True,
    )
    op.add_column("song", sa.Column("lastfm_mbid", sa.String(255), nullable=True))
    op.drop_column("song", "mbid")
    op.drop_column("song", "acoustid_fingerprint")
    op.drop_column("song", "acoustid_id")
    op.drop_column("song", "asin")
    op.drop_column("song", "replaygain_written")
    op.drop_column("song", "crest_factor")
    op.drop_column("song", "true_peak")
    op.drop_column("song", "loudness")
    op.drop_column("song", "musical_key")
    op.drop_column("song", "bpm")
    op.drop_column("song", "waveform")
    op.drop_column("song", "lyrics_synced")
    op.drop_column("song", "disc_no")
    op.drop_column("song", "intro_id")
    op.drop_column("song", "slug")

    op.drop_constraint("uq_album_slug", "album", type_="unique")
    op.add_column(
        "album", sa.Column("lastfm_mbid", sa.String(255), nullable=True)
    )
    op.drop_column("album", "mbid")
    op.drop_column("album", "disc_no")
    op.drop_column("album", "slug")

    op.drop_constraint("uq_artist_slug", "artist", type_="unique")
    op.add_column(
        "artist", sa.Column("lastfm_mbid", sa.String(64), nullable=True)
    )
    op.drop_column("artist", "founded_year")
    op.drop_column("artist", "mbid")
    op.drop_column("artist", "slug")

    op.drop_constraint("uq_genre_slug", "genre", type_="unique")
    op.drop_column("genre", "slug")
