import pytest

from hltex.errors import InvalidSyntax, UnexpectedEOF
from hltex.newtranslator import parse_group
from hltex.state import State


def test_parse_group():
    source = "something}123"
    state = State(source)
    assert state.run(parse_group, end="}") == "something"
    assert source[state.pos] == "1"


def test_parse_group_nested():
    source = "some{thi}ng}123"
    state = State(source)
    assert state.run(parse_group, end="}") == "some{thi}ng"
    assert source[state.pos] == "1"


def test_parse_group_missing():
    source = "some{thi}ng123"
    state = State(source)
    with pytest.raises(UnexpectedEOF) as excinfo:
        state.run(parse_group, end="}")
    assert "Missing closing `}`" in excinfo.value.msg


def test_parse_group_empty():
    source = "}123"
    state = State(source)
    assert state.run(parse_group, end="}") == ""
    assert source[state.pos] == "1"


def test_parse_group_control():
    source = "some\\thing}123"
    state = State(source)
    assert state.run(parse_group, end="}") == "some\\thing"
    assert source[state.pos] == "1"


def test_parse_group_control_args():
    source = "some\\thi{ni}ng}123"
    state = State(source)
    assert state.run(parse_group, end="}") == "some\\thi{ni}ng"
    assert source[state.pos] == "1"


def test_parse_group_control_optional_args():
    source = "some\\thi[ni]ng}123"
    state = State(source)
    assert state.run(parse_group, end="}") == "some\\thi[ni]ng"
    assert source[state.pos] == "1"


def test_parse_group_control_both_args():
    source = "some\\thi[ni]{ni}ng}123"
    state = State(source)
    assert state.run(parse_group, end="}") == "some\\thi[ni]{ni}ng"
    assert source[state.pos] == "1"


def test_parse_group_control_both_args_reversed():
    source = "some\\thi{ni}[ni]ng}123"
    state = State(source)
    assert state.run(parse_group, end="}") == "some\\thi{ni}[ni]ng"
    assert source[state.pos] == "1"


def test_parse_group_control_both_args_spaced():
    source = "some\\thi  {ni}  [ni]  ng}123"
    state = State(source)
    assert state.run(parse_group, end="}") == "some\\thi  {ni}  [ni]  ng"
    assert source[state.pos] == "1"


def test_parse_group_control_both_args_nested():
    source = "some\\thi{ni{ni}}[ni{ni}]ng}123"
    state = State(source)
    assert state.run(parse_group, end="}") == "some\\thi{ni{ni}}[ni{ni}]ng"
    assert source[state.pos] == "1"


def test_parse_group_control_both_args_nested_bracket():
    source = "some\\thi{ni{ni}}[ni{ni}ng]123"
    state = State(source)
    assert state.run(parse_group, end="]") == "some\\thi{ni{ni}}[ni{ni}ng"
    assert source[state.pos] == "1"


def test_parse_group_control_both_args_nested_bracket_escaped():
    source = "some\\thi{ni{ni}}\\[ni{ni}ng\\]]123"
    state = State(source)
    assert state.run(parse_group, end="]") == "some\\thi{ni{ni}}\\[ni{ni}ng\\]"
    assert source[state.pos] == "1"


def test_parse_group_control_both_args_nested_newline():
    source = "some\\thi\n\n{ni{ni}\n\n}[ni{\n\nni}]ng}123"
    state = State(source)
    assert state.run(parse_group, end="}") == "some\\thi\n\n{ni{ni}\n\n}[ni{\n\nni}]ng"
    assert source[state.pos] == "1"


def test_parse_group_control_both_args_unexpected():
    source = "some\\thi{ni{ni}}[ni{ni}}]ng}123"
    state = State(source)
    with pytest.raises(InvalidSyntax) as excinfo:
        state.run(parse_group, end="]")
    assert "Unexpected `}`" in excinfo.value.msg


def test_parse_group_comment():
    source = "some%thi\nng}123"
    state = State(source)
    assert state.run(parse_group, end="}") == "some%thi\nng"
    assert source[state.pos] == "1"
