from typing import Tuple
from unittest.mock import Mock, patch

import pytest

import wickedjukebox.xcom as xcom


@pytest.fixture
def fs():
    with patch("wickedjukebox.xcom.Path") as pth:
        state = xcom.FSState("fakedir")
        state.root = Mock()
        child_file = Mock()
        state.root.__truediv__ = Mock(return_value=child_file)
        yield state, child_file


def test_repr():
    state = xcom.NullState()
    assert "NullState" in repr(state)


def test_null_state():
    state = xcom.NullState()
    assert state.get(xcom.States.SKIP_REQUESTED) is None
    assert state.set(xcom.States.SKIP_REQUESTED, True) is None


@pytest.mark.parametrize("exist_state", [True, False])
def test_fsstate_get_skip(fs: Tuple[xcom.FSState, Mock], exist_state: bool):
    state, child_file = fs
    child_file.exists.return_value = exist_state  # type: ignore
    assert state.get(xcom.States.SKIP_REQUESTED) is exist_state


@pytest.mark.parametrize(
    "exist_state, new_state",
    [(True, True), (True, False), (False, True), (False, False)],
)
def test_fsstate_set_skip(
    fs: Tuple[xcom.FSState, Mock], exist_state: bool, new_state: bool
):
    state, child_file = fs
    child_file.exists.return_value = exist_state  # type: ignore
    state.set(xcom.States.SKIP_REQUESTED, new_state)
    if new_state:
        child_file.touch.assert_called()  # type: ignore
    else:
        if exist_state:
            child_file.unlink.assert_called()  # type: ignore


def test_fsstate_get_unknown(fs: Tuple[xcom.FSState, Mock]):
    state, _ = fs
    with pytest.raises(xcom.InvalidStateRequest):
        state.get("foobar")


def test_fsstate_set_unknown(fs: Tuple[xcom.FSState, Mock]):
    state, _ = fs
    with pytest.raises(xcom.InvalidStateRequest):
        state.set("foobar", "baz")
