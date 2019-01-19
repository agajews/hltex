import pytest

from hltex.errors import InvalidSyntax, UnexpectedEOF, UnexpectedIndentation
from hltex.newtranslator import parse_block
from hltex.state import State


def test_preamble():
    source = "\\documentclass{article}\n===\nHey!"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(res)
    assert res == "\\documentclass{article}\n\\begin{document}\nHey!\n\\end{document}"


def test_preamble_missing_document():
    source = "\\documentclass{article}\n==="
    state = State(source)
    with pytest.raises(UnexpectedEOF) as excinfo:
        parse_block(state, preamble=True)
    assert "Missing document body" in excinfo.value.msg


def test_preamble_missing_newline():
    source = "\\documentclass{article}\n===123"
    state = State(source)
    with pytest.raises(InvalidSyntax) as excinfo:
        parse_block(state, preamble=True)
    assert "Missing newline after document delineator" in excinfo.value.msg


def test_preamble_badly_indented():
    source = "\\documentclass{article}\n===\n  123"
    state = State(source)
    with pytest.raises(UnexpectedIndentation) as excinfo:
        parse_block(state, preamble=True)
    assert "document as a whole must not be indented" in excinfo.value.msg


def test_preamble_newline():
    source = "\\documentclass{article}\n===\nHey!\n"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(repr(res))
    assert res == "\\documentclass{article}\n\\begin{document}\nHey!\n\\end{document}"


def test_preamble_more_equals():
    source = "\\documentclass{article}\n======\n===Hey!\n"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(repr(res))
    assert (
        res == "\\documentclass{article}\n\\begin{document}\n===Hey!\n\\end{document}"
    )


def test_preamble_multiline():
    source = "\\documentclass{article}\n===\nHey!\nHey again!"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(res)
    assert (
        res
        == "\\documentclass{article}\n\\begin{document}\nHey!\nHey again!\n\\end{document}"
    )


def test_preamble_envs():
    source = "\\documentclass{article}\n\\eq:\n    f(x)\n===\nHey!\nHey again!"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(repr(res))
    assert (
        res
        == "\\documentclass{article}\n\\begin{eq}\n    f(x)\n\\end{eq}\n\\begin{document}\n    Hey!\n    Hey again!\n\\end{document}"
    )


def test_preamble_oneliners():
    source = "\\documentclass{article}\n\\eq:    f(x)\n===\nHey!\nHey again!"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(repr(res))
    assert (
        res
        == "\\documentclass{article}\n\\begin{eq}f(x)\\end{eq}\n\\begin{document}\nHey!\nHey again!\n\\end{document}"
    )
