import pytest

from hltex.errors import UnexpectedEOF
from hltex.newtranslator import parse_args
from hltex.state import State


def test_parse():
    source = "{arg1}{arg2}"
    state = State(source)
    assert parse_args(state, name="test", params="!") == ["arg1"]


def test_optional():
    source = "{arg1}[arg2]"
    state = State(source)
    assert parse_args(state, name="test", params="!?") == ["arg1", "arg2"]


def test_optional_whitespace():
    source = "  {  arg1  }  [  arg2  ]"
    state = State(source)
    assert parse_args(state, name="test", params="!?") == ["  arg1  ", "  arg2  "]


def test_optional_missing():
    source = "{arg1}{arg2}"
    state = State(source)
    assert parse_args(state, name="test", params="!?!") == ["arg1", None, "arg2"]


def test_missing():
    source = "{arg1}{arg2}"
    state = State(source)
    with pytest.raises(UnexpectedEOF) as excinfo:
        parse_args(state, name="test", params="!!!")
    assert "Missing required argument for `test`" in excinfo.value.msg
