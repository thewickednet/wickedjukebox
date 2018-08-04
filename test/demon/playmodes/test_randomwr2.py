from pytest_sqlalchemy import connection, dbsession, engine, transaction
from wickedjukebox.demon.playmodes import create


def test_random_wr2_standing_count(default_data, dbsession):
    instance = create('random_wr2', session=dbsession)
    result = instance._get_standing_count(
        default_data['default_song'].id,
        [default_data['default_user'].id],
        'love')
    assert result == 1

    result = instance._get_standing_count(
        default_data['default_song'].id,
        [default_data['default_user'].id],
        'hate')
    assert result == 0
