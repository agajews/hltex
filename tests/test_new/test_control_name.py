import pytest

from hltex.context import increment
from hltex.errors import UnexpectedEOF
from hltex.newtranslator import parse_control_name
from hltex.state import State


def test_name():
    source = "\\commandname123"
    state = State(source)
    increment(state)
    name = state.run(parse_control_name)
    assert name == "commandname"
    assert source[state.pos] == "1"


def test_name_end():
    source = "\\commandname"
    state = State(source)
    increment(state)
    name = state.run(parse_control_name)
    assert name == "commandname"
    assert state.pos == len(source)


def test_name_empty():
    source = "\\"
    state = State(source)
    increment(state)
    with pytest.raises(UnexpectedEOF) as excinfo:
        state.run(parse_control_name)
    assert (
        "Unescaped backslashes must be followed by at least one character"
        in excinfo.value.msg
    )


def test_symbol():
    source = "\\!stuff"
    state = State(source)
    increment(state)
    name = state.run(parse_control_name)
    assert name == "!"
    assert source[state.pos] == "s"


def test_colon():
    source = "\\:stuff"
    state = State(source)
    increment(state)
    name = state.run(parse_control_name)
    assert name == ":"
    assert source[state.pos] == "s"


def test_symbol_end():
    source = "\\!"
    state = State(source)
    increment(state)
    name = state.run(parse_control_name)
    assert name == "!"
    assert state.pos == 2


def test_colon_end():
    source = "\\:"
    state = State(source)
    increment(state)
    name = state.run(parse_control_name)
    assert name == ":"
    assert state.pos == 2
