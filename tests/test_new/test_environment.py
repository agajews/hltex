from hltex.newcontrol import Environment
from hltex.newtranslator import parse_environment_body, parse_native_control
from hltex.state import State


def test_parse_native_control():
    source = "123"
    state = State(source)
    assert (
        state.run(parse_native_control, name="something", outer_indent_level=0)
        == "\\something"
    )
    assert source[state.pos] == "1"


def test_parse_native_control_args():
    source = "{arg1}{arg2}123"
    state = State(source)
    assert (
        state.run(parse_native_control, name="something", outer_indent_level=0)
        == "\\something{arg1}{arg2}"
    )
    assert source[state.pos] == "1"


def test_parse_native_control_args_whitespace():
    source = "  {arg1}  {arg2}  123"
    state = State(source)
    assert (
        state.run(parse_native_control, name="something", outer_indent_level=0)
        == "\\something  {arg1}  {arg2}"
    )
    assert state.pos == 16


def test_parse_native_control_args_optional():
    source = "{arg1}[arg2]123"
    state = State(source)
    assert (
        state.run(parse_native_control, name="something", outer_indent_level=0)
        == "\\something{arg1}[arg2]"
    )
    assert source[state.pos] == "1"


def test_parse_native_control_env():
    source = "{arg1}{arg2}:\n    some words"
    state = State(source)
    assert (
        state.run(parse_native_control, name="something", outer_indent_level=0)
        == "\\begin{something}{arg1}{arg2}\n    some words\n\\end{something}"
    )
    assert state.pos == len(source)


def test_parse_environment_body():
    source = "something\n"
    state = State(source)
    assert state.run(parse_environment_body, outer_indent_level=0) == "something"
    assert source[state.pos] == "\n"


def test_parse_environment_body_eof():
    source = "something"
    state = State(source)
    assert state.run(parse_environment_body, outer_indent_level=0) == "something"
    assert state.pos == len(source)


def test_parse_environment_body_command():
    source = "some\\thi{n}g\n"
    state = State(source)
    assert state.run(parse_environment_body, outer_indent_level=0) == "some\\thi{n}g"
    assert source[state.pos] == "\n"


def test_parse_environment_body_indented():
    source = "\n    something"
    state = State(source)
    assert state.run(parse_environment_body, outer_indent_level=0) == "\n    something"
    assert state.pos == len(source)


def test_parse_environment_body_indented_multiline():
    source = "\n    something\n    something else"
    state = State(source)
    assert (
        state.run(parse_environment_body, outer_indent_level=0)
        == "\n    something\n    something else"
    )
    assert state.pos == len(source)


def test_parse_environment_body_indented_multiline_empty():
    source = "\n    something\n    something else\n   \n  "
    state = State(source)
    assert (
        state.run(parse_environment_body, outer_indent_level=0)
        == "\n    something\n    something else\n   \n  "
    )
    assert state.pos == len(source)


def test_parse_environment_body_indented_multiline_empty_not_eof():
    source = "\n    something\n    something else\n   \n  \n123"
    state = State(source)
    res = state.run(parse_environment_body, outer_indent_level=0)
    print(repr(res))
    assert res == "\n    something\n    something else\n   \n  \n"
    assert source[state.pos] == "1"
