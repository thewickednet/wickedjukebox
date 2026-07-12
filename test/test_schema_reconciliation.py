# type: ignore
# pylint: skip-file
"""Assert the daemon's built schema matches the django-reconciled index set.

Introspects the live (alembic-built) schema via SQLAlchemy. Guards against
re-drift: the daemon-required uniques Django under-declares are asserted KEPT,
and the phantom/low-value indexes are asserted GONE.
"""

from sqlalchemy import inspect


def _index_names(insp, table):
    names = {ix["name"] for ix in insp.get_indexes(table)}
    names |= {uc["name"] for uc in insp.get_unique_constraints(table)}
    return names


def _index_colsets(insp, table):
    return {tuple(ix["column_names"]) for ix in insp.get_indexes(table)}


def _unique_colsets(insp, table):
    sets = {
        tuple(ix["column_names"])
        for ix in insp.get_indexes(table)
        if ix.get("unique")
    }
    sets |= {
        tuple(uc["column_names"]) for uc in insp.get_unique_constraints(table)
    }
    return sets


def test_song_indexes_reconciled(dbsession):
    insp = inspect(dbsession.get_bind())
    names = _index_names(insp, "song")
    # ADDED composite, KEPT mood index
    assert ("available", "broken") in _index_colsets(insp, "song")
    assert "song_mood_score_idx" in names
    # DROPPED low-value single-column indexes
    assert "broken" not in names
    assert "title" not in names
    assert "exclude_from_random" not in names
    # KEPT daemon-required unique Django under-declares
    assert ("localpath",) in _unique_colsets(insp, "song")


def test_album_indexes_reconciled(dbsession):
    insp = inspect(dbsession.get_bind())
    names = _index_names(insp, "album")
    assert "name" not in names
    assert "type" not in names
    assert ("path",) in _unique_colsets(insp, "album")


def test_artist_name_unique_kept(dbsession):
    insp = inspect(dbsession.get_bind())
    # keep-list: artist.name UNIQUE is daemon-required (Artist.by_name uses
    # .one_or_none()); Django under-declares it, so guard against re-drift.
    assert ("name",) in _unique_colsets(insp, "artist")


def test_channel_song_data_indexes_reconciled(dbsession):
    insp = inspect(dbsession.get_bind())
    # redundant single channel_id gone; composite (channel_id, song_id) kept
    assert ("channel_id",) not in _index_colsets(insp, "channel_song_data")
    assert ("channel_id", "song_id") in _unique_colsets(
        insp, "channel_song_data"
    )


def test_song_pk_is_autoincrement(dbsession):
    insp = inspect(dbsession.get_bind())
    id_col = next(c for c in insp.get_columns("song") if c["name"] == "id")
    assert id_col.get("autoincrement") is True


def test_queue_and_setting_indexes_reconciled(dbsession):
    insp = inspect(dbsession.get_bind())
    assert ("position",) not in _index_colsets(insp, "queue")
    # single var gone; (var, channel_id, user_id) composite unique kept
    assert ("var",) not in _index_colsets(insp, "setting")
    assert ("var", "channel_id", "user_id") in _unique_colsets(insp, "setting")
