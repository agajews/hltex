from hltex.newtranslator import parse_native_control
from hltex.state import State


def test_parse():
    source = "123"
    state = State(source)
    assert (
        state.run(parse_native_control, name="something", outer_indent_level=0)
        == "\\something"
    )
    assert source[state.pos] == "1"


def test_args():
    source = "{arg1}{arg2}123"
    state = State(source)
    assert (
        state.run(parse_native_control, name="something", outer_indent_level=0)
        == "\\something{arg1}{arg2}"
    )
    assert source[state.pos] == "1"


def test_args_whitespace():
    source = "  {arg1}  {arg2}  123"
    state = State(source)
    assert (
        state.run(parse_native_control, name="something", outer_indent_level=0)
        == "\\something  {arg1}  {arg2}"
    )
    assert state.pos == 16


def test_args_optional():
    source = "{arg1}[arg2]123"
    state = State(source)
    assert (
        state.run(parse_native_control, name="something", outer_indent_level=0)
        == "\\something{arg1}[arg2]"
    )
    assert source[state.pos] == "1"


def test_one_liner():
    source = "{arg1}{arg2}:    some words"
    state = State(source)
    res = state.run(parse_native_control, name="something", outer_indent_level=0)
    print(repr(res))
    assert res == "\\begin{something}{arg1}{arg2}some words\\end{something}"
    assert state.pos == len(source)


def test_one_liner_newline():
    source = "{arg1}{arg2}: some words\n"
    state = State(source)
    assert (
        state.run(parse_native_control, name="something", outer_indent_level=0)
        == "\\begin{something}{arg1}{arg2}some words\\end{something}"
    )
    assert source[state.pos] == "\n"


def test_one_liner_newline_empty():
    source = "{arg1}{arg2}:    some words\n  "
    state = State(source)
    res = state.run(parse_native_control, name="something", outer_indent_level=0)
    print(repr(res))
    assert res == "\\begin{something}{arg1}{arg2}some words\\end{something}"
    assert source[state.pos] == "\n"


def test_env():
    source = "{arg1}{arg2}:\n    some words"
    state = State(source)
    assert (
        state.run(parse_native_control, name="something", outer_indent_level=0)
        == "\\begin{something}{arg1}{arg2}\n    some words\n\\end{something}"
    )
    assert state.pos == len(source)
