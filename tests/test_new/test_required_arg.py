import pytest

from hltex.errors import MissingArgument, UnexpectedEOF
from hltex.newtranslator import parse_required_arg
from hltex.state import State


def test_parse():
    source = "{something}123"
    state = State(source)
    assert state.run(parse_required_arg, name="test") == "something"
    assert source[state.pos] == "1"


def test_raw():
    source = "{something}123"
    state = State(source)
    assert state.run(parse_required_arg, name="test", raw=True) == "something"
    assert source[state.pos] == "1"


def test_raw_missing():
    source = "{somethi{ng}123"
    state = State(source)
    assert state.run(parse_required_arg, name="test", raw=True) == "somethi{ng"
    assert source[state.pos] == "1"


def test_raw_newline():
    source = "{somethi\nng}123"
    state = State(source)
    assert state.run(parse_required_arg, name="test", raw=True) == "somethi\nng"
    assert source[state.pos] == "1"


def test_whitespace():
    source = "  {  something  }  123"
    state = State(source)
    assert state.run(parse_required_arg, name="test") == "  something  "
    assert source[state.pos] == " "


def test_missing():
    source = "  something  ]  123"
    state = State(source)
    with pytest.raises(MissingArgument) as excinfo:
        state.run(parse_required_arg, name="test")
    assert "Missing required argument for `test`" in excinfo.value.msg


def test_end():
    source = ""
    state = State(source)
    with pytest.raises(UnexpectedEOF) as excinfo:
        state.run(parse_required_arg, name="test")
    assert "Missing required argument for `test`" in excinfo.value.msg
