import wickedjukebox.demon.playmodes.queue_positioned as queue
from wickedjukebox.demon.dbmodel import QueueItem, Song
import pytest


@pytest.fixture
def queue_data(default_data, dbsession):
    for _ in range(3):
        queue.enqueue(
            dbsession,
            default_data["default_song"].id,
            default_data["default_user"].id,
            default_data["default_channel"].id,
        )
    yield default_data


def test_enqueue(queue_data, dbsession):
    result = queue.enqueue(
        dbsession,
        queue_data["default_song"].id,
        queue_data["default_user"].id,
        queue_data["default_channel"].id,
    )
    dbsession.flush()
    count = dbsession.query(QueueItem).count()
    assert count == 4


def test_list(queue_data, dbsession):
    result = queue.list(dbsession, queue_data["default_channel"].id)
    assert len(result) == 3


def test_dequeue(queue_data, dbsession):
    dequeued_song = queue.dequeue(dbsession, queue_data["default_channel"].id)
    dbsession.flush()
    positions = [row.position for row in dbsession.query(QueueItem)]
    assert isinstance(dequeued_song, Song)
    # positions should have shifted down by one
    assert positions == [0, 1, 2]


def test_moveup(queue_data, dbsession):
    items = [row for row in dbsession.query(QueueItem)]
    queue.moveup(dbsession, queue_data["default_channel"].id, items[2].id, 1)
    positions = [row.position for row in dbsession.query(QueueItem)]
    assert positions == [1, 3, 2]


def test_movedown(queue_data, dbsession):
    items = [row for row in dbsession.query(QueueItem)]
    queue.movedown(dbsession, queue_data["default_channel"].id, items[0].id, 1)
    positions = [row.position for row in dbsession.query(QueueItem)]
    assert positions == [2, 1, 3]


def test_movetop(dbsession):
    with pytest.raises(NotImplementedError):
        queue.movetop(dbsession, 0, 0)


def test_movebottom(dbsession):
    with pytest.raises(NotImplementedError):
        queue.movebottom(dbsession, 0, 0)
