# type: ignore
# pylint: skip-file
"""add song.exclude_from_random

Add a per-song boolean flag that hard-excludes a song from the random /
autoplay picker (sibling to ``broken``). Defined NOT NULL DEFAULT 0 so that
NULL is never treated as falsy by the ``not_(...)`` filter. Explicit
queueing is unaffected.

Revision ID: c7a1e9b4f2d3
Revises: b3d9f1a2c4e6
Create Date: 2026-07-02
"""

import sqlalchemy as sa

from alembic import op

revision = "c7a1e9b4f2d3"
down_revision = "b3d9f1a2c4e6"


def upgrade():
    op.add_column(
        "song",
        sa.Column(
            "exclude_from_random",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.create_index(
        "exclude_from_random",
        "song",
        ["exclude_from_random"],
        unique=False,
    )


def downgrade():
    op.drop_index("exclude_from_random", table_name="song")
    op.drop_column("song", "exclude_from_random")
