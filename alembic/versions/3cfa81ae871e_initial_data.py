"""initial-data

Revision ID: 3cfa81ae871e
Revises: 3f2143a67fcf
Create Date: 2017-07-27 05:50:29.169110

"""

from textwrap import dedent

from alembic import op


# revision identifiers, used by Alembic.
revision = '3cfa81ae871e'
down_revision = '3f2143a67fcf'


def upgrade():
    op.execute('ALTER TABLE channel_album_data AUTO_INCREMENT = 0')
    op.execute('ALTER TABLE channel AUTO_INCREMENT = 0')
    op.execute('ALTER TABLE users AUTO_INCREMENT = 0')
    op.execute('ALTER TABLE groups AUTO_INCREMENT = 0')
    op.execute("SET SESSION sql_mode='NO_AUTO_VALUE_ON_ZERO'")

    op.execute(dedent(
        """\
        INSERT INTO channel (
            id, name, backend, backend_params
        ) VALUES (
            0,
            'wicked',
            'icecast',
            'port=8001, mount=/wicked.mp3, pwd=mussdulauschtren, admin_url=http://localhost:8001/admin, admin_username=admin, admin_password=matourenstepp'
        )
        """))
    op.execute(dedent(
        '''\
        INSERT INTO groups (
            id,
            title,
            admin
        ) VALUES (
            0,
            'admin',
            1
        )'''))
    op.execute(dedent(
        '''\
        INSERT INTO users (
            id,
            username,
            cookie,
            password,
            fullname,
            email,
            credits,
            group_id,
            added,
            proof_of_life,
            proof_of_listening,
            IP,
            picture,
            lifetime,
            channel_id
        ) VALUES (
            0,
            'admin',
            '',
            'admin',
            'Admin admin',
            'admin@wickedjukebox.com',
            90,
            0,
            NOW(),
            NOW(),
            NOW(),
            '',
            '',
            0,
            0
        )
        '''))
    op.execute("INSERT INTO setting (var, value) VALUES "
               "('max_random_duration', 600),"
               "('mediadir', '/var/mp3/Tagged'),"
               "('proofoflife_timeout', 120),"
               "('queue_model', 'queue_positioned'),"
               "('random_model', 'random_wr2'),"
               "('recency_threshold', 120),"
               "('recognizedTypes', 'mp3'),"
               "('scoring_lastPlayed', 4),"
               "('scoring_neverPlayed', 4),"
               "('scoring_randomness', 1),"
               "('scoring_songAge', 0),"
               "('scoring_userRating', 6),"
               "('shoutbox', 1),"
               "('songs_threshold', 2),"
               "('sys_utctime', 1)")


def downgrade():
    op.execute('DELETE FROM channel_album_data')
    op.execute('DELETE FROM channel')
    op.execute('DELETE FROM users')
    op.execute('DELETE FROM groups')
    op.execute('DELETE FROM setting')

    op.execute('ALTER TABLE channel_album_data AUTO_INCREMENT = 0')
    op.execute('ALTER TABLE channel AUTO_INCREMENT = 0')
    op.execute('ALTER TABLE users AUTO_INCREMENT = 0')
    op.execute('ALTER TABLE groups AUTO_INCREMENT = 0')
