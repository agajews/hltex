from textwrap import dedent
import pytest
from hltex.translator import Translator, TranslationError

def translate(source):
    translator = Translator(source)
    return translator.translate()

def test_hello():
    source = dedent('''
    \\documentclass{article}
    \\document:
    Hello?
    ''')
    assert translate(source) == dedent(
    '''
    \\documentclass{article}
    \\begin{document}
    Hello?
    \\end{document}''')


def test_parse_while():
    source = 'aaaaabbbb'
    translator = Translator(source)
    translator.parse_while(lambda c: c == 'a')
    assert source[translator.pos] == 'b'
    assert translator.pos == 5


def test_parse_while_none():
    source = 'aaaaabbbb'
    translator = Translator(source)
    translator.parse_while(lambda c: False)
    assert translator.pos == 0


def test_parse_until():
    source = 'aaaaabbbb'
    translator = Translator(source)
    translator.parse_until(lambda c: c == 'b')
    assert source[translator.pos] == 'b'
    assert translator.pos == 5


def test_parse_until_none():
    source = 'aaaaabbbb'
    translator = Translator(source)
    translator.parse_until(lambda c: False)
    assert translator.pos == len(source)


def test_validate_indent_good():
    source = 'aaaaabbbb'
    translator = Translator(source)
    translator.validate_indent('    ')
    translator.validate_indent('\t\t\t\t')
    translator.validate_indent('')


def test_validate_indent_bad():
    source = 'aaaaabbbb'
    translator = Translator(source)
    with pytest.raises(TranslationError) as excinfo:
        translator.validate_indent('    \t')
    assert 'Invalid indentation' in excinfo.value.msg


def test_level_of_indent():
    source = 'aaaaabbbb'
    translator = Translator(source)
    translator.indent_str = '    '
    assert translator.level_of_indent('') == 0
    assert translator.level_of_indent('    ') == 1
    assert translator.level_of_indent('            ') == 3

    with pytest.raises(TranslationError) as excinfo:
        translator.level_of_indent('   ')
    assert 'Indentation must be in multiples' in excinfo.value.msg


def test_calc_indent_level_first():
    source = 'some text'
    translator = Translator(source)
    # translator.indent_str = '    '
    assert translator.calc_indent_level() == 0


def test_calc_indent_level_good():
    source = '    some text'
    translator = Translator(source)
    translator.indent_str = '    '
    assert translator.calc_indent_level() == 1
    assert source[translator.pos] == 's'


def test_calc_indent_level_empty():
    source = '    \n    some text'
    translator = Translator(source)
    translator.indent_str = '    '
    assert translator.calc_indent_level() == 1
    assert source[translator.pos] == '\n'


def test_calc_indent_level_end():
    source = '    '
    translator = Translator(source)
    translator.indent_str = '    '
    assert translator.calc_indent_level() == 1
    assert translator.pos == 4

def test_calc_indent_level_double():
    source = '        some text'
    translator = Translator(source)
    translator.indent_str = '    '
    with pytest.raises(TranslationError) as excinfo:
        translator.calc_indent_level()
    assert 'one level at a time' in excinfo.value.msg


def test_calc_indent_level_bad():
    source = '   some text'
    translator = Translator(source)
    translator.indent_str = '    '
    with pytest.raises(TranslationError) as excinfo:
        translator.calc_indent_level()
    assert 'multiples of the base' in excinfo.value.msg


