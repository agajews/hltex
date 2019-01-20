import pytest

from hltex.errors import InvalidSyntax
from hltex.state import State
from hltex.translator import parse_optional_argstr


def test_parse():
    source = "something]123"
    state = State(source)
    assert state.run(parse_optional_argstr) == "something"
    assert source[state.pos] == "1"


def test_nested():
    source = "some{thi}ng]123"
    state = State(source)
    assert state.run(parse_optional_argstr) == "some{thi}ng"
    assert source[state.pos] == "1"


def test_missing():
    source = "some{thi}ng123"
    state = State(source)
    assert state.run(parse_optional_argstr) is None
    assert state.pos == 0


def test_empty():
    source = "]123"
    state = State(source)
    assert state.run(parse_optional_argstr) == ""
    assert source[state.pos] == "1"


def test_control():
    source = "some\\thing]123"
    state = State(source)
    assert state.run(parse_optional_argstr) == "some\\thing"
    assert source[state.pos] == "1"


def test_control_args():
    source = "some\\thi{ni}ng]123"
    state = State(source)
    assert state.run(parse_optional_argstr) == "some\\thi{ni}ng"
    assert source[state.pos] == "1"


def test_control_optional_args():
    source = "some\\thi[ni]ng]123"
    state = State(source)
    assert state.run(parse_optional_argstr) == "some\\thi[ni]ng"
    assert source[state.pos] == "1"


def test_control_both_args():
    source = "some\\thi[ni]{ni}ng]123"
    state = State(source)
    assert state.run(parse_optional_argstr) == "some\\thi[ni]{ni}ng"
    assert source[state.pos] == "1"


def test_control_both_args_reversed():
    source = "some\\thi{ni}[ni]ng]123"
    state = State(source)
    assert state.run(parse_optional_argstr) == "some\\thi{ni}[ni]ng"
    assert source[state.pos] == "1"


def test_control_both_args_spaced():
    source = "some\\thi  {ni}  [ni]  ng]123"
    state = State(source)
    assert state.run(parse_optional_argstr) == "some\\thi  {ni}  [ni]  ng"
    assert source[state.pos] == "1"


def test_control_both_args_nested():
    source = "some\\thi{ni{ni}}[ni{ni}]ng]123"
    state = State(source)
    assert state.run(parse_optional_argstr) == "some\\thi{ni{ni}}[ni{ni}]ng"
    assert source[state.pos] == "1"


def test_control_both_args_nested_bracket():
    source = "some\\thi{ni{ni}}[ni{ni}ng]]123"
    state = State(source)
    assert state.run(parse_optional_argstr) == "some\\thi{ni{ni}}[ni{ni}ng]"
    assert source[state.pos] == "1"


def test_control_both_args_nested_bracket_escaped():
    source = "some\\thi{ni{ni}}\\[ni{ni}ng\\]]123"
    state = State(source)
    assert state.run(parse_optional_argstr) == "some\\thi{ni{ni}}\\[ni{ni}ng\\]"
    assert source[state.pos] == "1"


def test_control_both_args_nested_newline_none():
    source = "some\\thi\n\n{ni{ni}\n\n}[ni{\n\nni}]ng]123"
    state = State(source)
    assert state.run(parse_optional_argstr) is None
    assert state.pos == 0


def test_control_both_args_unexpected():
    source = "some\\thi{ni{ni}}[ni{ni}}]ng}123"
    state = State(source)
    with pytest.raises(InvalidSyntax) as excinfo:
        state.run(parse_optional_argstr)
    assert "Unexpected `}`" in excinfo.value.msg
