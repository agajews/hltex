import pytest

from hltex.errors import InvalidSyntax
from hltex.newtranslator import parse_block
from hltex.state import State


def test_parse():
    source = "something"
    state = State(source)
    assert state.run(parse_block) == "something"
    assert state.pos == len(source)


def test_newline():
    source = "something\n"
    state = State(source)
    assert state.run(parse_block) == "something"
    assert source[state.pos] == "\n"


def test_indented():
    source = "    some{thi}ng"
    state = State(source)
    assert state.run(parse_block) == "    some{thi}ng"
    assert state.pos == len(source)


def test_indented_newline():
    source = "    some{thi}ng\n"
    state = State(source)
    assert state.run(parse_block) == "    some{thi}ng"
    assert source[state.pos] == "\n"


def test_indented_newline_empty():
    source = "    some{thi}ng\n  "
    state = State(source)
    assert state.run(parse_block) == "    some{thi}ng"
    assert source[state.pos] == "\n"


def test_indented_multiline():
    source = "    some{thi}ng\n    another\\thi{ng}\n"
    state = State(source)
    res = state.run(parse_block)
    print(res)
    assert res == "    some{thi}ng\n    another\\thi{ng}"
    assert source[state.pos] == "\n"


def test_indented_multiline_empty():
    source = "    some{thi}ng\n   \n    another\\thi{ng}\n"
    state = State(source)
    res = state.run(parse_block)
    print(res)
    assert res == "    some{thi}ng\n   \n    another\\thi{ng}"
    assert source[state.pos] == "\n"


def test_eof():
    source = ""
    state = State(source)
    res = state.run(parse_block)
    print(res)
    assert res == ""
    assert state.pos == len(source)


def test_indented_eof():
    source = "    "
    state = State(source)
    res = state.run(parse_block)
    print(res)
    assert res == "    "
    assert state.pos == len(source)


def test_indented_empty():
    source = "    \n   "
    state = State(source)
    res = state.run(parse_block)
    print(res)
    assert res == "    \n   "
    assert state.pos == len(source)


def test_group_newline():
    source = "    some{\nthi\n}ng"
    state = State(source)
    assert state.run(parse_block) == "    some{\nthi\n}ng"
    assert state.pos == len(source)


def test_control_args():
    source = "    some\\thi{ni}{ng}\n    123"
    state = State(source)
    assert state.run(parse_block) == "    some\\thi{ni}{ng}\n    123"
    assert state.pos == len(source)


def test_control_both_args():
    source = "    some\\thi[ni]{ni}ng\n    123"
    state = State(source)
    assert state.run(parse_block) == "    some\\thi[ni]{ni}ng\n    123"
    assert state.pos == len(source)


def test_control_both_args_reversed():
    source = "    some\\thi{ni}[ni]ng\n    123"
    state = State(source)
    assert state.run(parse_block) == "    some\\thi{ni}[ni]ng\n    123"
    assert state.pos == len(source)


def test_control_both_args_newline():
    source = "    some\\thi\n    [\n    ni\n    ]{\nni\n}ng\n    123"
    state = State(source)
    assert (
        state.run(parse_block)
        == "    some\\thi\n    [\n    ni\n    ]{\nni\n}ng\n    123"
    )
    assert state.pos == len(source)


def test_control_both_args_newline_not_indented():
    source = "    some\\thi\n    [\nni\n    ]{\nni\n}ng\n    123"
    state = State(source)
    assert state.run(parse_block) == "    some\\thi\n    ["
    assert source[state.pos] == "\n"


def test_indented_not_end():
    source = "    some\\thi[ni]{ni}ng\n123"
    state = State(source)
    assert state.run(parse_block) == "    some\\thi[ni]{ni}ng"
    assert source[state.pos] == "\n"


def test_indented_not_end_empty():
    source = "    some\\thi[ni]{ni}ng\n   \n  \n123"
    state = State(source)
    assert state.run(parse_block) == "    some\\thi[ni]{ni}ng"
    assert source[state.pos] == "\n"


def test_nested():
    source = "\\eq:\n  \\split:\n    \\textbf{Hello}"
    state = State(source)
    res = state.run(parse_block)
    print(res)
    assert (
        res
        == "\\begin{eq}\n  \\begin{split}\n    \\textbf{Hello}\n  \\end{split}\n\\end{eq}"
    )
    assert state.pos == len(source)


def test_nested_not_start():
    source = "123\\eq:\n  \\split:\n    \\textbf{Hello}"
    state = State(source)
    res = state.run(parse_block)
    print(repr(res))
    assert (
        res
        == "123\\begin{eq}\n  \\begin{split}\n    \\textbf{Hello}\n  \\end{split}\n\\end{eq}"
    )
    assert state.pos == len(source)


def test_control_both_args_spaced():
    source = "    some\\thi  {ni}  [ni]  ng\n123"
    state = State(source)
    assert state.run(parse_block) == "    some\\thi  {ni}  [ni]  ng"
    assert source[state.pos] == "\n"


def test_control_both_args_nested():
    source = "    some\\thi{\nni{\nni\n}\n}\n    [ni{\nni\n}]ng\n    more things\n123"
    state = State(source)
    assert (
        state.run(parse_block)
        == "    some\\thi{\nni{\nni\n}\n}\n    [ni{\nni\n}]ng\n    more things"
    )
    assert source[state.pos] == "\n"


def test_control_both_args_nested_bracket_escaped():
    source = "    some\\thi{ni{ni}}\\[ni{ni}ng\\]\n123"
    state = State(source)
    assert state.run(parse_block) == "    some\\thi{ni{ni}}\\[ni{ni}ng\\]"
    assert source[state.pos] == "\n"


def test_control_both_args_unexpected():
    source = "some\\thi{ni{ni}}[ni{ni}}]ng}123"
    state = State(source)
    with pytest.raises(InvalidSyntax) as excinfo:
        state.run(parse_block)
    assert "Unexpected `}`" in excinfo.value.msg


def test_not_eof():
    source = "\\eq:\n  \\textbf{Hello}\n123"
    state = State(source)
    res = state.run(parse_block)
    print(res)
    assert res == "\\begin{eq}\n  \\textbf{Hello}\n\\end{eq}\n123"
    assert state.pos == len(source)


def test_stacked():
    source = "\\eq:\n  \\textbf{Hello}\n\\eq:\n  f(x)\n123"
    state = State(source)
    res = state.run(parse_block)
    print(res)
    assert (
        res
        == "\\begin{eq}\n  \\textbf{Hello}\n\\end{eq}\n\\begin{eq}\n  f(x)\n\\end{eq}\n123"
    )
    assert state.pos == len(source)


def test_stacked_comment():
    source = (
        "\\eq: %something\n  \\textbf{Hello}%more\n  %something\n\\eq:\n  f(x)\n123"
    )
    state = State(source)
    res = state.run(parse_block)
    print(res)
    assert (
        res
        == "\\begin{eq}\n  %something\n  \\textbf{Hello}%more\n  %something\n\\end{eq}\n\\begin{eq}\n  f(x)\n\\end{eq}\n123"
    )
    assert state.pos == len(source)


def test_onliner_stacked():
    source = "\\eq: \\textbf{Hello}\n\\eq: f(x)\n123"
    state = State(source)
    res = state.run(parse_block)
    print(res)
    assert res == "\\begin{eq}\\textbf{Hello}\\end{eq}\n\\begin{eq}f(x)\\end{eq}\n123"
    assert state.pos == len(source)
