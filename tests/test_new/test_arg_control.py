import pytest

from hltex.context import increment
from hltex.errors import UnexpectedEOF
from hltex.newcontrol import Command
from hltex.newtranslator import parse_arg_control
from hltex.state import State


def test_parse():
    source = "\\somename123"
    state = State(source)
    increment(state)
    assert state.run(parse_arg_control) == "\\somename"
    assert source[state.pos] == "1"


def test_end():
    source = "\\somename"
    state = State(source)
    increment(state)
    assert state.run(parse_arg_control) == "\\somename"
    assert state.pos == len(source)


def test_symbol():
    source = "\\:123"
    state = State(source)
    increment(state)
    assert state.run(parse_arg_control) == "\\:"
    assert source[state.pos] == "1"


def test_symbol_end():
    source = "\\:"
    state = State(source)
    increment(state)
    assert state.run(parse_arg_control) == "\\:"
    assert state.pos == len(source)


def test_empty():
    source = "\\"
    state = State(source)
    increment(state)
    with pytest.raises(UnexpectedEOF) as excinfo:
        state.run(parse_arg_control)
    assert "Unescaped backslashes" in excinfo.value.msg


def test_custom_command():
    source = "\\some{\\thing{arg1}}123"

    def thing_translate_fn(_state, a):
        return "\\textbf{%s}" % a

    def some_translate_fn(_state, a):
        return "\\textsl{%s}" % a

    state = State(source)
    increment(state)
    state.commands["thing"] = Command("thing", thing_translate_fn, "!")
    state.commands["some"] = Command("some", some_translate_fn, "!")
    assert state.run(parse_arg_control) == "\\textsl{\\textbf{arg1}}"
