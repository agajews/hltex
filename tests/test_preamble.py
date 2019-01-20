import pytest

from hltex.errors import InvalidSyntax, UnexpectedEOF, UnexpectedIndentation
from hltex.state import State
from hltex.translator import parse_block


def test_parse():
    source = "\\documentclass{article}\n===\nHey!"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(res)
    assert res == "\\documentclass{article}\n\\begin{document}\nHey!\n\\end{document}"


def test_parse_start():
    source = "===\nHey!"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(res)
    assert res == "\\begin{document}\nHey!\n\\end{document}"


def test_parse_double_newline():
    source = "\\documentclass{article}\n\n===\nHey!"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(res)
    assert res == "\\documentclass{article}\n\n\\begin{document}\nHey!\n\\end{document}"


def test_parse_empty_after():
    source = "\\documentclass{article}\n===\n  \n"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(res)
    assert res == "\\documentclass{article}\n\\begin{document}\n\n\\end{document}"


def test_parse_double_newline_after_preamble():
    source = "\\documentclass{article}\n===\n\nHey!"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(res)
    assert res == "\\documentclass{article}\n\\begin{document}\n\nHey!\n\\end{document}"


def test_missing_document():
    source = "\\documentclass{article}\n==="
    state = State(source)
    with pytest.raises(UnexpectedEOF) as excinfo:
        parse_block(state, preamble=True)
    assert "Missing document body" in excinfo.value.msg


def test_missing_newline():
    source = "\\documentclass{article}\n===123"
    state = State(source)
    with pytest.raises(InvalidSyntax) as excinfo:
        parse_block(state, preamble=True)
    assert "Missing newline after document delineator" in excinfo.value.msg


def test_badly_indented():
    source = "\\documentclass{article}\n===\n  123"
    state = State(source)
    with pytest.raises(UnexpectedIndentation) as excinfo:
        parse_block(state, preamble=True)
    assert "document as a whole must not be indented" in excinfo.value.msg


def test_newline():
    source = "\\documentclass{article}\n===\nHey!\n"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(repr(res))
    assert res == "\\documentclass{article}\n\\begin{document}\nHey!\n\\end{document}"


def test_more_equals():
    source = "\\documentclass{article}\n======\n===Hey!\n"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(repr(res))
    assert (
        res == "\\documentclass{article}\n\\begin{document}\n===Hey!\n\\end{document}"
    )


def test_multiline():
    source = "\\documentclass{article}\n===\nHey!\nHey again!"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(res)
    assert (
        res
        == "\\documentclass{article}\n\\begin{document}\nHey!\nHey again!\n\\end{document}"
    )


def test_envs():
    source = "\\documentclass{article}\n\\equation:\n    f(x)\n===\nHey!\nHey again!"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(repr(res))
    assert (
        res
        == "\\documentclass{article}\n\\begin{equation}\n    f(x)\n\\end{equation}\n\\begin{document}\nHey!\nHey again!\n\\end{document}"
    )


def test_oneliners():
    source = "\\documentclass{article}\n\\equation:    f(x)\n===\nHey!\nHey again!"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(repr(res))
    assert (
        res
        == "\\documentclass{article}\n\\begin{equation}f(x)\\end{equation}\n\\begin{document}\nHey!\nHey again!\n\\end{document}"
    )
