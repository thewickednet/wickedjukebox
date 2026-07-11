# type: ignore
# pylint: skip-file
"""mood range parity

Map the mood columns created by djukebox (Django migrations 0042/0043) into
the alembic-managed schema: song.mood_score (composite energy score 0-100,
computed by djukebox) and channel.mood_low/mood_high (the randomizer mood
window). Production already has these columns (its schema is Django-managed)
— this migration only serves alembic-built dev/test databases, exactly like
the djukebox_field_parity precedent (b3d9f1a2c4e6).

Revision ID: e8f2a4c6d0b1
Revises: c7a1e9b4f2d3
Create Date: 2026-07-11
"""

import sqlalchemy as sa

from alembic import op

revision = "e8f2a4c6d0b1"
down_revision = "c7a1e9b4f2d3"


def upgrade():
    op.add_column(
        "song", sa.Column("mood_score", sa.SmallInteger(), nullable=True)
    )
    op.create_index("song_mood_score_idx", "song", ["mood_score"], unique=False)
    op.add_column(
        "channel", sa.Column("mood_low", sa.SmallInteger(), nullable=True)
    )
    op.add_column(
        "channel", sa.Column("mood_high", sa.SmallInteger(), nullable=True)
    )


def downgrade():
    op.drop_column("channel", "mood_high")
    op.drop_column("channel", "mood_low")
    op.drop_index("song_mood_score_idx", table_name="song")
    op.drop_column("song", "mood_score")
