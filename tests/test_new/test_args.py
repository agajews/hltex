import pytest

from hltex.errors import UnexpectedEOF
from hltex.newtranslator import parse_args
from hltex.state import State


def test_parse():
    source = "{arg1}{arg2}"
    state = State(source)
    assert parse_args(state, name="test", params="!") == ["arg1"]
    assert state.pos == 6


def test_parse_not_eof():
    source = "{arg1}{arg2} 123"
    state = State(source)
    assert parse_args(state, name="test", params="!!") == ["arg1", "arg2"]
    assert source[state.pos] == " "


def test_none():
    source = "123"
    state = State(source)
    assert parse_args(state, name="test", params="") == []
    assert state.pos == 0


def test_none_eof():
    source = ""
    state = State(source)
    assert parse_args(state, name="test", params="") == []
    assert state.pos == 0


def test_optional():
    source = "{arg1}[arg2]"
    state = State(source)
    assert parse_args(state, name="test", params="!?") == ["arg1", "arg2"]
    assert state.pos == len(source)


def test_optional_whitespace():
    source = "  {  arg1  }  [  arg2  ]"
    state = State(source)
    assert parse_args(state, name="test", params="!?") == ["  arg1  ", "  arg2  "]
    assert state.pos == len(source)


def test_optional_missing():
    source = "{arg1}{arg2}"
    state = State(source)
    assert parse_args(state, name="test", params="!?!") == ["arg1", None, "arg2"]
    assert state.pos == len(source)


def test_optional_all_missing():
    source = "123"
    state = State(source)
    assert parse_args(state, name="test", params="?") == [None]
    assert source[state.pos] == "1"


def test_missing():
    source = "{arg1}{arg2}"
    state = State(source)
    with pytest.raises(UnexpectedEOF) as excinfo:
        parse_args(state, name="test", params="!!!")
    assert "Missing required argument for `test`" in excinfo.value.msg
