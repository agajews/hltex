import pytest

from hltex.errors import InvalidIndentation
from hltex.indentation import (
    calc_indent_level,
    level_of_indent,
    line_is_empty,
    validate_indent,
)
from hltex.state import State


def test_validate_indent_good():
    state = State("", indent_str="    ")
    validate_indent(state, "    ")
    state = State("", indent_str="\t\t\t\t")
    validate_indent(state, "\t\t\t\t")
    state = State("", indent_str="    ")
    validate_indent(state, "")


def test_validate_indent_bad():
    state = State("", indent_str="    ")
    with pytest.raises(InvalidIndentation) as excinfo:
        validate_indent(state, "    \t")
    assert "Indentation must be all spaces or all tabs" in excinfo.value.msg
    with pytest.raises(InvalidIndentation) as excinfo:
        validate_indent(state, "   ")
    assert (
        "Indentation must be in multiples of the base indentation" in excinfo.value.msg
    )


def test_level_of_indent():
    state = State("", indent_str="    ")
    assert level_of_indent(state, "        ") == 2
    assert level_of_indent(state, "") == 0
    state = State("", indent_str="\t\t")
    assert level_of_indent(state, "\t\t\t\t") == 2


def test_calc_indent_level():
    source = """    hi"""
    state = State(source, indent_str="    ")
    assert calc_indent_level(state) == 1


def test_calc_indent_level_empty():
    source = """hi"""
    state = State(source)
    assert calc_indent_level(state) == 0


def test_calc_indent_level_zero():
    source = """hi"""
    state = State(source, indent_str="    ")
    assert calc_indent_level(state) == 0


def test_calc_indent_level_two():
    source = """        hi"""
    state = State(source, indent_str="    ")
    assert calc_indent_level(state) == 2


def test_calc_indent_level_none():
    source = """    hi"""
    state = State(source)
    assert calc_indent_level(state) == 1
    assert state.indent_str == "    "


def test_calc_indent_level_bad():
    source = """   hi"""
    state = State(source, indent_str="    ")
    with pytest.raises(InvalidIndentation) as excinfo:
        calc_indent_level(state)
    assert (
        "Indentation must be in multiples of the base indentation" in excinfo.value.msg
    )


def test_line_is_empty():
    source = """    \n123"""
    state = State(source)
    assert line_is_empty(state)
    assert state.pos == 0


def test_line_is_empty_newline():
    source = """    \n"""
    state = State(source)
    assert line_is_empty(state)
    assert state.pos == 0


def test_line_is_empty_eof():
    source = """    """
    state = State(source)
    assert line_is_empty(state)
    assert state.pos == 0


def test_line_is_empty_tabs():
    source = """  \t """
    state = State(source)
    assert line_is_empty(state)
    assert state.pos == 0


def test_line_is_empty_not():
    source = """    123\n456"""
    state = State(source)
    assert not line_is_empty(state)
    assert state.pos == 0
