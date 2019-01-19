import pytest

from hltex.context import increment
from hltex.errors import UnexpectedIndentation
from hltex.newtranslator import parse_raw_environment_body
from hltex.state import State


def test_parse():
    source = ":something\n"
    state = State(source)
    increment(state)
    assert parse_raw_environment_body(state, outer_indent_level=0) == "something"
    assert source[state.pos] == "\n"


def test_unmatched():
    source = ":somethi{ng\n"
    state = State(source)
    increment(state)
    assert parse_raw_environment_body(state, outer_indent_level=0) == "somethi{ng"
    assert source[state.pos] == "\n"


def test_comment():
    source = ":somethi%ng\n"
    state = State(source)
    increment(state)
    assert parse_raw_environment_body(state, outer_indent_level=0) == "somethi%ng"
    assert source[state.pos] == "\n"


def test_eof():
    source = ":something"
    state = State(source)
    increment(state)
    assert parse_raw_environment_body(state, outer_indent_level=0) == "something"
    assert state.pos == len(source)


def test_not_eof():
    source = ":something\n123"
    state = State(source)
    increment(state)
    assert parse_raw_environment_body(state, outer_indent_level=0) == "something"
    assert source[state.pos] == "\n"


def test_block():
    source = ":\n    something\n123"
    state = State(source)
    increment(state)
    assert parse_raw_environment_body(state, outer_indent_level=0) == "\n    something"
    assert source[state.pos] == "\n"


def test_block_eof():
    source = ":\n    something\n"
    state = State(source)
    increment(state)
    assert (
        parse_raw_environment_body(state, outer_indent_level=0) == "\n    something\n"
    )
    assert state.pos == len(source)


def test_block_multiline():
    source = ":\n    something\n    something else\n123"
    state = State(source)
    increment(state)
    assert (
        parse_raw_environment_body(state, outer_indent_level=0)
        == "\n    something\n    something else"
    )
    assert source[state.pos] == "\n"


def test_block_empty():
    source = ":\n    something\n   \n    something else\n123"
    state = State(source)
    increment(state)
    assert (
        parse_raw_environment_body(state, outer_indent_level=0)
        == "\n    something\n   \n    something else"
    )
    assert source[state.pos] == "\n"


def test_unexpected_indentation():
    source = ":\n    something\n   \n        something else\n123"
    state = State(source)
    increment(state)
    with pytest.raises(UnexpectedIndentation) as excinfo:
        parse_raw_environment_body(state, outer_indent_level=0)
    assert "Indentation should only follow environments" in excinfo.value.msg
