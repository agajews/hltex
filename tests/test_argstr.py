import pytest

from hltex.errors import UnexpectedEOF
from hltex.state import State
from hltex.translator import parse_argstr


def test_parse():
    source = "{something}123"
    state = State(source)
    assert state.run(parse_argstr) == "{something}"
    assert source[state.pos] == "1"


def test_multiple():
    source = "{something}[else]{more things}123"
    state = State(source)
    assert state.run(parse_argstr) == "{something}[else]{more things}"
    assert source[state.pos] == "1"


def test_multiple_whitespace():
    source = "  {something}  [else]  {more things}  123"
    state = State(source)
    assert state.run(parse_argstr) == "  {something}  [else]  {more things}"
    assert state.pos == 36


def test_multiple_newline():
    source = "  {something}  [else] \n{more things}  123"
    state = State(source)
    assert state.run(parse_argstr) == "  {something}  [else]"
    assert state.pos == 21


def test_optional_missing():
    source = "  {something}  [else \n{more things}  123"
    state = State(source)
    assert state.run(parse_argstr) == "  {something}"
    assert state.pos == 13


def test_empty():
    source = "123"
    state = State(source)
    assert state.run(parse_argstr) == ""
    assert source[state.pos] == "1"


def test_eof():
    source = ""
    state = State(source)
    assert state.run(parse_argstr) == ""
    assert state.pos == 0


def test_unexpected_eof():
    source = "{123"
    state = State(source)
    with pytest.raises(UnexpectedEOF) as excinfo:
        state.run(parse_argstr)
    assert "Missing closing `}`" in excinfo.value.msg


def test_optional():
    source = "[something]123"
    state = State(source)
    assert state.run(parse_argstr) == "[something]"
    assert source[state.pos] == "1"


def test_optional_comment():
    source = "{something}[somethi%]123\nng]123"
    state = State(source)
    assert state.run(parse_argstr) == "{something}"
    assert source[state.pos] == "["


def test_optional_nested():
    source = "[some\\thi[n]g]123"
    state = State(source)
    assert state.run(parse_argstr) == "[some\\thi[n]g]"
    assert source[state.pos] == "1"


def test_optional_escaped():
    source = "[some\\thi\\[n]g]123"
    state = State(source)
    assert state.run(parse_argstr) == "[some\\thi\\[n]"
    assert source[state.pos] == "g"


def test_optional_escaped_whitespace():
    source = "  [some  \\thi  \\[  n  ]  g  ]  123"
    state = State(source)
    assert state.run(parse_argstr) == "  [some  \\thi  \\[  n  ]"
    assert source[state.pos] == " "
