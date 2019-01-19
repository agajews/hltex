import pytest

from hltex.errors import UnexpectedIndentation
from hltex.newtranslator import parse_raw_environment_body
from hltex.state import State


def test_parse_raw_environment_body():
    source = "something\n"
    state = State(source)
    assert parse_raw_environment_body(state, outer_indent_level=0) == "something"
    assert source[state.pos] == "\n"


def test_parse_raw_environment_body_unmatched():
    source = "somethi{ng\n"
    state = State(source)
    assert parse_raw_environment_body(state, outer_indent_level=0) == "somethi{ng"
    assert source[state.pos] == "\n"


def test_parse_raw_environment_body_comment():
    source = "somethi%ng\n"
    state = State(source)
    assert parse_raw_environment_body(state, outer_indent_level=0) == "somethi%ng"
    assert source[state.pos] == "\n"


def test_parse_raw_environment_body_eof():
    source = "something"
    state = State(source)
    assert parse_raw_environment_body(state, outer_indent_level=0) == "something"
    assert state.pos == len(source)


def test_parse_raw_environment_body_not_eof():
    source = "something\n123"
    state = State(source)
    assert parse_raw_environment_body(state, outer_indent_level=0) == "something"
    assert source[state.pos] == "\n"


def test_parse_raw_environment_body_block():
    source = "\n    something\n123"
    state = State(source)
    assert parse_raw_environment_body(state, outer_indent_level=0) == "\n    something"
    assert source[state.pos] == "\n"


def test_parse_raw_environment_body_block_multiline():
    source = "\n    something\n    something else\n123"
    state = State(source)
    assert (
        parse_raw_environment_body(state, outer_indent_level=0)
        == "\n    something\n    something else"
    )
    assert source[state.pos] == "\n"


def test_parse_raw_environment_body_block_empty():
    source = "\n    something\n   \n    something else\n123"
    state = State(source)
    assert (
        parse_raw_environment_body(state, outer_indent_level=0)
        == "\n    something\n   \n    something else"
    )
    assert source[state.pos] == "\n"


def test_parse_raw_environment_body_unexpected_indentation():
    source = "\n    something\n   \n        something else\n123"
    state = State(source)
    with pytest.raises(UnexpectedIndentation) as excinfo:
        parse_raw_environment_body(state, outer_indent_level=0)
    assert "Indentation should only follow environments" in excinfo.value.msg
