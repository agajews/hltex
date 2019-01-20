from hltex.control import Environment
from hltex.state import State
from hltex.translator import parse_custom_environment


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


def test_parse_raw():
    source = ": \\ H}ey"
    state = State(source)

    def translate_fn(_state, body):
        return "\\begin{itemize}\\item %s\\end{itemize}" % body

    res = parse_custom_environment(
        state, Environment("test", translate_fn, "", raw=True), 0
    )
    print(repr(res))
    assert res == "\\begin{itemize}\\item \\ H}ey\\end{itemize}"
    assert state.pos == len(source)


def test_newline_raw():
    source = ": \\ H}ey\n"
    state = State(source)

    def translate_fn(_state, body):
        return "\\begin{itemize}\\item %s\\end{itemize}" % body

    res = parse_custom_environment(
        state, Environment("test", translate_fn, "", raw=True), 0
    )
    print(repr(res))
    assert res == "\\begin{itemize}\\item \\ H}ey\\end{itemize}"
    assert source[state.pos] == "\n"


def test_not_eof_raw():
    source = ": \\ H}ey\n123"
    state = State(source)

    def translate_fn(_state, body):
        return "\\begin{itemize}\\item %s\\end{itemize}" % body

    res = parse_custom_environment(
        state, Environment("test", translate_fn, "", raw=True), 0
    )
    print(repr(res))
    assert res == "\\begin{itemize}\\item \\ H}ey\\end{itemize}"
    assert source[state.pos] == "\n"


def test_block_raw():
    source = ":\n  H}ey\n  H{ey again\n123"
    state = State(source)

    def translate_fn(_state, body):
        return "\\begin{itemize}\\item %s\\end{itemize}" % body

    res = parse_custom_environment(
        state, Environment("test", translate_fn, "", raw=True), 0
    )
    print(repr(res))
    assert res == "\\begin{itemize}\\item \nH}ey\nH{ey again\n\\end{itemize}"
    assert source[state.pos] == "\n"


def test_block_eof_raw():
    source = ":\n  H}ey\n  H{ey again"
    state = State(source)

    def translate_fn(_state, body):
        return "\\begin{itemize}\\item %s\\end{itemize}" % body

    res = parse_custom_environment(
        state, Environment("test", translate_fn, "", raw=True), 0
    )
    print(repr(res))
    assert res == "\\begin{itemize}\\item \nH}ey\nH{ey again\n\\end{itemize}"
    assert state.pos == len(source)
