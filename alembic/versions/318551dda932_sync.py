# type: ignore
# pylint: skip-file
"""
sync

Revision ID: 318551dda932
Revises: 7c6b18d72ff3
Create Date: 2021-12-31 16:55:56.185117
"""

# revision identifiers, used by Alembic.
revision = "318551dda932"
down_revision = "7c6b18d72ff3"

import sqlalchemy as sa

from alembic import op


def upgrade():
    op.create_foreign_key(
        "song_has_tag_song_id",
        "song_has_tag",
        "song",
        ["song_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "song_has_tag_tag_id",
        "song_has_tag",
        "tag",
        ["tag_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "user_song_standing_song_id",
        "user_song_standing",
        "song",
        ["song_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "user_song_standing_user_id",
        "user_song_standing",
        "users",
        ["user_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint(
        "user_song_standing_user_id", "user_song_standing", type_="foreignkey"
    )
    op.drop_constraint(
        "user_song_standing_song_id", "user_song_standing", type_="foreignkey"
    )
    op.drop_constraint(
        "song_has_tag_tag_id", "song_has_tag", type_="foreignkey"
    )
    op.drop_constraint(
        "song_has_tag_song_id", "song_has_tag", type_="foreignkey"
    )
