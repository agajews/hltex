from hltex.context import parse_until, parse_while
from hltex.state import State


def test_parse_while():
    source = "aaaaabbbb"
    state = State(source)
    state.run(parse_while, pred=lambda c: c == "a")
    assert source[state.pos] == "b"
    assert state.pos == 5


def test_parse_while_none():
    source = "aaaaabbbb"
    state = State(source)
    state.run(parse_while, pred=lambda c: False)
    assert source[state.pos] == "a"
    assert state.pos == 0


def test_parse_until():
    source = "aaaaabbbb"
    state = State(source)
    state.run(parse_until, pred=lambda c: c == "b")
    assert source[state.pos] == "b"
    assert state.pos == 5


def test_parse_until_none():
    source = "aaaaabbbb"
    state = State(source)
    state.run(parse_until, pred=lambda c: False)
    assert state.pos == len(source)
