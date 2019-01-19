from hltex.context import increment
from hltex.newtranslator import parse_environment_body
from hltex.state import State


def test_parse():
    source = ":something\n"
    state = State(source)
    increment(state)
    res = state.run(parse_environment_body, outer_indent_level=0)
    print(repr(res))
    assert res == "something"
    assert source[state.pos] == "\n"


def test_group():
    source = ":some{\nstuff\n}thing\n123"
    state = State(source)
    increment(state)
    res = state.run(parse_environment_body, outer_indent_level=0)
    print(repr(res))
    assert res == "some{\nstuff\n}thing"
    assert source[state.pos] == "\n"


def test_comment():
    source = ":some%thing\n123"
    state = State(source)
    increment(state)
    res = state.run(parse_environment_body, outer_indent_level=0)
    print(repr(res))
    assert res == "some%thing"
    assert source[state.pos] == "\n"


def test_eof():
    source = ":something"
    state = State(source)
    increment(state)
    assert state.run(parse_environment_body, outer_indent_level=0) == "something"
    assert state.pos == len(source)


def test_command():
    source = ":some\\thi{n}g\n"
    state = State(source)
    increment(state)
    assert state.run(parse_environment_body, outer_indent_level=0) == "some\\thi{n}g"
    assert source[state.pos] == "\n"


def test_indented():
    source = ":\n    something"
    state = State(source)
    increment(state)
    assert state.run(parse_environment_body, outer_indent_level=0) == "\n    something"
    assert state.pos == len(source)


def test_indented_multiline():
    source = ":\n    something\n    something else"
    state = State(source)
    increment(state)
    assert (
        state.run(parse_environment_body, outer_indent_level=0)
        == "\n    something\n    something else"
    )
    assert state.pos == len(source)


def test_indented_multiline_newline():
    source = ":\n    something\n    something else\n"
    state = State(source)
    increment(state)
    assert (
        state.run(parse_environment_body, outer_indent_level=0)
        == "\n    something\n    something else"
    )
    assert source[state.pos] == "\n"


def test_indented_multiline_empty():
    source = ":\n    something\n    something else\n   \n  "
    state = State(source)
    increment(state)
    assert (
        state.run(parse_environment_body, outer_indent_level=0)
        == "\n    something\n    something else"
    )
    assert source[state.pos] == "\n"


def test_indented_multiline_empty_not_eof():
    source = ":\n    something\n    something else\n   \n  \n123"
    state = State(source)
    increment(state)
    res = state.run(parse_environment_body, outer_indent_level=0)
    print(repr(res))
    assert res == "\n    something\n    something else"
    assert source[state.pos] == "\n"
