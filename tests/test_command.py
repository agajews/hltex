from hltex.control import Command
from hltex.state import State
from hltex.translator import parse_custom_command


def test_arg_control():
    source = "{arg1}[arg2]{arg3}123"
    state = State(source)

    def translate_fn(_state, a, b, c):
        return "\\textbf{%s} %s \\textsl{%s}" % (a, b, c)

    assert (
        state.run(parse_custom_command, command=Command("test", translate_fn, "!?!"))
        == "\\textbf{arg1} arg2 \\textsl{arg3}"
    )
    assert source[state.pos] == "1"


def test_arg_control_whitespace():
    source = "  {arg1}  [arg2]  {arg3}  123"
    state = State(source)

    def translate_fn(_state, a, b, c):
        return "\\textbf{%s} %s \\textsl{%s}" % (a, b, c)

    assert (
        state.run(parse_custom_command, command=Command("test", translate_fn, "!?!"))
        == "\\textbf{arg1} arg2 \\textsl{arg3}"
    )
    assert state.pos == 24


def test_arg_control_none():
    source = "{arg1}{arg3}123"
    state = State(source)

    def translate_fn(_state, a, b, c):
        assert b is None
        return "\\textbf{%s} \\textsl{%s}" % (a, c)

    assert (
        state.run(parse_custom_command, command=Command("test", translate_fn, "!?!"))
        == "\\textbf{arg1} \\textsl{arg3}"
    )
    assert source[state.pos] == "1"
