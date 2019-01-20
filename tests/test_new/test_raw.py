from hltex.context import increment
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
    source = ":\n    something"
    state = State(source)
    increment(state)
    assert parse_raw_environment_body(state, outer_indent_level=0) == "\n    something"
    assert state.pos == len(source)


def test_block_eof_multiline():
    source = ":\n    something\n    something else"
    state = State(source)
    increment(state)
    assert (
        parse_raw_environment_body(state, outer_indent_level=0)
        == "\n    something\n    something else"
    )
    assert state.pos == len(source)


def test_block_multiline_empty_eof():
    source = ":\n    something\n    something else\n  \n"
    state = State(source)
    increment(state)
    assert (
        parse_raw_environment_body(state, outer_indent_level=0)
        == "\n    something\n    something else"
    )
    assert source[state.pos] == "\n"


def test_block_multiline_empty_eof_no_newline():
    source = ":\n    something\n    something else\n  "
    state = State(source)
    increment(state)
    assert (
        parse_raw_environment_body(state, outer_indent_level=0)
        == "\n    something\n    something else"
    )
    assert source[state.pos] == "\n"


def test_block_multiline_empty_eof_more_after():
    source = ":\n    something\n    something else\n  \n123"
    state = State(source)
    increment(state)
    assert (
        parse_raw_environment_body(state, outer_indent_level=0)
        == "\n    something\n    something else"
    )
    assert source[state.pos] == "\n"


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
    source = ":\n    something\n   \n        something else\n    more things\n123"
    state = State(source)
    increment(state)
    assert (
        parse_raw_environment_body(state, outer_indent_level=0)
        == "\n    something\n   \n        something else\n    more things"
    )
    assert source[state.pos] == "\n"
