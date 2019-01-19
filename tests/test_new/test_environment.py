from hltex.newcontrol import Environment
from hltex.newtranslator import parse_custom_environment
from hltex.state import State


def test_parse():
    source = ": \\ Hey"
    state = State(source)

    def translate_fn(_state, body):
        return "\\begin{itemize}\\item %s\\end{itemize}" % body

    res = parse_custom_environment(state, Environment("test", translate_fn, ""), 0)
    print(repr(res))
    assert res == "\\begin{itemize}\\item \\ Hey\\end{itemize}"
    assert state.pos == len(source)


def test_newline():
    source = ": \\ Hey\n"
    state = State(source)

    def translate_fn(_state, body):
        return "\\begin{itemize}\\item %s\\end{itemize}" % body

    res = parse_custom_environment(state, Environment("test", translate_fn, ""), 0)
    print(repr(res))
    assert res == "\\begin{itemize}\\item \\ Hey\\end{itemize}"
    assert source[state.pos] == "\n"


def test_not_eof():
    source = ": \\ Hey\n123"
    state = State(source)

    def translate_fn(_state, body):
        return "\\begin{itemize}\\item %s\\end{itemize}" % body

    res = parse_custom_environment(state, Environment("test", translate_fn, ""), 0)
    print(repr(res))
    assert res == "\\begin{itemize}\\item \\ Hey\\end{itemize}"
    assert source[state.pos] == "\n"


def test_block():
    source = ":\n  Hey\n  Hey again\n123"
    state = State(source)

    def translate_fn(_state, body):
        return "\\begin{itemize}\\item %s\\end{itemize}" % body

    res = parse_custom_environment(state, Environment("test", translate_fn, ""), 0)
    print(repr(res))
    assert res == "\\begin{itemize}\\item \nHey\nHey again\n\\end{itemize}"
    assert source[state.pos] == "\n"


def test_block_eof():
    source = ":\n  Hey\n  Hey again"
    state = State(source)

    def translate_fn(_state, body):
        return "\\begin{itemize}\\item %s\\end{itemize}" % body

    res = parse_custom_environment(state, Environment("test", translate_fn, ""), 0)
    print(repr(res))
    assert res == "\\begin{itemize}\\item \nHey\nHey again\n\\end{itemize}"
    assert state.pos == len(source)
