import pytest

from hltex.errors import UnexpectedEOF
from hltex.newtranslator import parse_argstr
from hltex.state import State


def test_parse_argstr():
    source = "{something}123"
    state = State(source)
    assert state.run(parse_argstr) == "{something}"
    assert source[state.pos] == "1"


def test_parse_argstr_multiple():
    source = "{something}[else]{more things}123"
    state = State(source)
    assert state.run(parse_argstr) == "{something}[else]{more things}"
    assert source[state.pos] == "1"


def test_parse_argstr_multiple_whitespace():
    source = "  {something}  [else]  {more things}  123"
    state = State(source)
    assert state.run(parse_argstr) == "  {something}  [else]  {more things}"
    assert state.pos == 36


def test_parse_argstr_multiple_newline():
    source = "  {something}  [else] \n{more things}  123"
    state = State(source)
    assert state.run(parse_argstr) == "  {something}  [else]"
    assert state.pos == 21


def test_parse_argstr_optional_missing():
    source = "  {something}  [else \n{more things}  123"
    state = State(source)
    assert state.run(parse_argstr) == "  {something}"
    assert state.pos == 13


def test_parse_argstr_empty():
    source = "123"
    state = State(source)
    assert state.run(parse_argstr) == ""
    assert source[state.pos] == "1"


def test_parse_argstr_eof():
    source = ""
    state = State(source)
    assert state.run(parse_argstr) == ""
    assert state.pos == 0


def test_parse_argstr_unexpected_eof():
    source = "{123"
    state = State(source)
    with pytest.raises(UnexpectedEOF) as excinfo:
        state.run(parse_argstr)
    assert "Missing closing `}`" in excinfo.value.msg


def test_parse_argstr_optional():
    source = "[something]123"
    state = State(source)
    assert state.run(parse_argstr) == "[something]"
    assert source[state.pos] == "1"


def test_parse_argstr_optional_comment():
    source = "{something}[somethi%]123\nng]123"
    state = State(source)
    assert state.run(parse_argstr) == "{something}"
    assert source[state.pos] == "["


def test_parse_argstr_optional_nested():
    source = "[some\\thi[n]g]123"
    state = State(source)
    assert state.run(parse_argstr) == "[some\\thi[n]g]"
    assert source[state.pos] == "1"


def test_parse_argstr_optional_escaped():
    source = "[some\\thi\\[n]g]123"
    state = State(source)
    assert state.run(parse_argstr) == "[some\\thi\\[n]"
    assert source[state.pos] == "g"


def test_parse_argstr_optional_escaped_whitespace():
    source = "  [some  \\thi  \\[  n  ]  g  ]  123"
    state = State(source)
    assert state.run(parse_argstr) == "  [some  \\thi  \\[  n  ]"
    assert source[state.pos] == " "
