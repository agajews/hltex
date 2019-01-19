from hltex.newtranslator import parse_optional_arg
from hltex.state import State


def test_parse():
    source = "[something]123"
    state = State(source)
    assert state.run(parse_optional_arg) == "something"
    assert source[state.pos] == "1"


def test_whitespace():
    source = "  [  something  ]  123"
    state = State(source)
    assert state.run(parse_optional_arg) == "  something  "
    assert source[state.pos] == " "


def test_missing():
    source = "  something  ]  123"
    state = State(source)
    assert state.run(parse_optional_arg) is None
    assert state.pos == 0


def test_end():
    source = ""
    state = State(source)
    assert state.run(parse_optional_arg) is None
    assert state.pos == 0
