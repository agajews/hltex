# import pytest

# from hltex.errors import InvalidSyntax, UnexpectedEOF
from hltex.newtranslator import parse_block
from hltex.state import State


def test_preamble():
    source = "\\documentclass{article}\n===\nHey!"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(res)
    assert res == "\\documentclass{article}\n\\begin{document}\nHey!\n\\end{document}\n"


def test_preamble_newline():
    source = "\\documentclass{article}\n===\nHey!\n"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(repr(res))
    assert res == "\\documentclass{article}\n\\begin{document}\nHey!\n\\end{document}\n"


def test_preamble_multiline():
    source = "\\documentclass{article}\n===\nHey!\nHey again!"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(res)
    assert (
        res
        == "\\documentclass{article}\n\\begin{document}\nHey!\nHey again!\n\\end{document}\n"
    )


def test_preamble_envs():
    source = "\\documentclass{article}\n\\eq:\n    f(x)\n===\nHey!\nHey again!"
    state = State(source)
    res = parse_block(state, preamble=True)
    print(repr(res))
    assert (
        res
        == "\\documentclass{article}\n\\begin{eq}\n    f(x)\n\\end{eq}\n\\begin{document}\n    Hey!\n    Hey again!\n\\end{document}\n"
    )
