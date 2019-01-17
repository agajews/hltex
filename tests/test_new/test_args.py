import pytest

from hltex.errors import MissingArgument, UnexpectedEOF
from hltex.newcontrol import Command
from hltex.newtranslator import (
    parse_arg_control,
    parse_args,
    parse_optional_arg,
    parse_required_arg,
)
from hltex.state import State


def test_arg_control():
    source = "somename123"
    state = State(source)
    assert state.run(parse_arg_control) == "\\somename"
    assert source[state.pos] == "1"


def test_arg_control_end():
    source = "somename"
    state = State(source)
    assert state.run(parse_arg_control) == "\\somename"
    assert state.pos == len(source)


def test_arg_control_symbol():
    source = ":123"
    state = State(source)
    assert state.run(parse_arg_control) == "\\:"
    assert source[state.pos] == "1"


def test_arg_control_symbol_end():
    source = ":"
    state = State(source)
    assert state.run(parse_arg_control) == "\\:"
    assert state.pos == len(source)


def test_arg_control_empty():
    source = ""
    state = State(source)
    with pytest.raises(UnexpectedEOF) as excinfo:
        state.run(parse_arg_control)
    assert "Unescaped backslashes" in excinfo.value.msg


def test_arg_control_custom_command():
    source = "some{\\thing{arg1}}123"

    def thing_translate_fn(_state, a):
        return "\\textbf{%s}" % a

    def some_translate_fn(_state, a):
        return "\\textsl{%s}" % a

    state = State(source)
    state.commands["thing"] = Command("thing", thing_translate_fn, "!")
    state.commands["some"] = Command("some", some_translate_fn, "!")
    assert state.run(parse_arg_control) == "\\textsl{\\textbf{arg1}}"


def test_optional_arg():
    source = "[something]123"
    state = State(source)
    assert state.run(parse_optional_arg) == "something"
    assert source[state.pos] == "1"


def test_optional_arg_whitespace():
    source = "  [  something  ]  123"
    state = State(source)
    assert state.run(parse_optional_arg) == "  something  "
    assert source[state.pos] == " "


def test_optional_arg_missing():
    source = "  something  ]  123"
    state = State(source)
    assert state.run(parse_optional_arg) is None
    assert state.pos == 0


def test_optional_arg_end():
    source = ""
    state = State(source)
    assert state.run(parse_optional_arg) is None
    assert state.pos == 0


def test_required_arg():
    source = "{something}123"
    state = State(source)
    assert state.run(parse_required_arg, name="test") == "something"
    assert source[state.pos] == "1"


def test_required_arg_whitespace():
    source = "  {  something  }  123"
    state = State(source)
    assert state.run(parse_required_arg, name="test") == "  something  "
    assert source[state.pos] == " "


def test_required_arg_missing():
    source = "  something  ]  123"
    state = State(source)
    with pytest.raises(MissingArgument) as excinfo:
        state.run(parse_required_arg, name="test")
    assert "Missing required argument for `test`" in excinfo.value.msg


def test_required_arg_end():
    source = ""
    state = State(source)
    with pytest.raises(UnexpectedEOF) as excinfo:
        state.run(parse_required_arg, name="test")
    assert "Missing required argument for `test`" in excinfo.value.msg


def test_parse_args():
    source = "{arg1}{arg2}"
    state = State(source)
    assert parse_args(state, name="test", params="!") == ["arg1"]


def test_parse_args_optional():
    source = "{arg1}[arg2]"
    state = State(source)
    assert parse_args(state, name="test", params="!?") == ["arg1", "arg2"]


def test_parse_args_optional_whitespace():
    source = "  {  arg1  }  [  arg2  ]"
    state = State(source)
    assert parse_args(state, name="test", params="!?") == ["  arg1  ", "  arg2  "]


def test_parse_args_optional_missing():
    source = "{arg1}{arg2}"
    state = State(source)
    assert parse_args(state, name="test", params="!?!") == ["arg1", None, "arg2"]


def test_parse_args_missing():
    source = "{arg1}{arg2}"
    state = State(source)
    with pytest.raises(UnexpectedEOF) as excinfo:
        parse_args(state, name="test", params="!!!")
    assert "Missing required argument for `test`" in excinfo.value.msg
