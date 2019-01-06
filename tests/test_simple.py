from textwrap import dedent
import pytest
from hltex.translator import Translator, TranslationError, Arg

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


def test_parse_empty_good():
    source = '    \n\n    some text'
    translator = Translator(source)
    translator.parse_empty()
    assert translator.pos == 6


def test_parse_empty_stay():
    source = '    some text'
    translator = Translator(source)
    translator.parse_empty()
    assert translator.pos == 0


def test_parse_empty_none():
    source = '    \n\n  \n   '
    translator = Translator(source)
    translator.parse_empty()
    assert translator.pos == len(source)


def test_get_control_seq():
    source = 'commandname123'
    translator = Translator(source)
    assert translator.get_control_seq() == 'commandname'
    assert source[translator.pos] == '1'


def test_get_control_seq_end():
    source = 'commandname'
    translator = Translator(source)
    assert translator.get_control_seq() == 'commandname'
    assert translator.pos == len(source)


def test_get_control_symbol():
    source = '!stuff'
    translator = Translator(source)
    assert translator.get_control_seq() == '!'
    assert source[translator.pos] == 's'


def test_get_control_colon():
    source = ':stuff'
    translator = Translator(source)
    assert translator.get_control_seq() == ':'
    assert source[translator.pos] == 's'


def test_get_control_symbol_end():
    source = '!'
    translator = Translator(source)
    assert translator.get_control_seq() == '!'
    assert translator.pos == 1


def test_get_control_colon_end():
    source = ':'
    translator = Translator(source)
    assert translator.get_control_seq() == ':'
    assert translator.pos == 1


def test_extract_arg():
    source = 'my \nargument}some more text'
    translator = Translator(source)
    assert translator.extract_arg() == 'my \nargument'
    assert source[translator.pos] == 's'


def test_extract_arg_end():
    source = 'my \nargument}'
    translator = Translator(source)
    assert translator.extract_arg() == 'my \nargument'
    assert translator.pos == len(source)


def test_extract_arg_opt():
    source = 'my \nargument]some more text'
    translator = Translator(source)
    assert translator.extract_arg(']') == 'my \nargument'
    assert source[translator.pos] == 's'


def test_extract_arg_opt_end():
    source = 'my \nargument]'
    translator = Translator(source)
    assert translator.extract_arg(']') == 'my \nargument'
    assert translator.pos == len(source)


# TODO: test extract_arg with nested commands


def test_extract_arg_unmatched():
    source = 'my argument'
    translator = Translator(source)
    with pytest.raises(TranslationError) as excinfo:
        translator.extract_arg(required=True)
    assert 'Missing closing' in excinfo.value.msg


def test_extract_arg_opt_unmatched():
    source = 'my argument'
    translator = Translator(source)
    assert translator.extract_arg() == None
    assert translator.pos == len(source)


def test_extract_args():
    source = '{arg1}{arg2}some text'
    translator = Translator(source)
    args, argstr = translator.extract_args()
    assert args == [Arg('arg1'), Arg('arg2')]
    assert argstr == '{arg1}{arg2}'
    assert source[translator.pos] == 's'


def test_extract_args_opt():
    source = '{arg1}[arg2]{arg1}some text'
    translator = Translator(source)
    args, argstr = translator.extract_args()
    assert args == [Arg('arg1'), Arg('arg2', optional=True), Arg('arg1')]
    assert argstr == '{arg1}[arg2]{arg1}'
    assert source[translator.pos] == 's'


def test_extract_args_whitespace():
    # NOTE: this is different from standard LaTeX, where newlines don't matter
    # we can still parse standard latex like this, but our commands have to have
    # their arguments on the same line
    source = ' {arg1}  [arg2]\n{arg1}some text'
    translator = Translator(source)
    args, argstr = translator.extract_args()
    assert args == [Arg('arg1'), Arg('arg2', optional=True)]
    assert argstr == ' {arg1}  [arg2]'
    assert source[translator.pos] == '\n'


def test_extract_args_opt_unmatched():
    source = '{arg1[}[arg2{arg1}some text'
    translator = Translator(source)
    args, argstr = translator.extract_args()
    assert args == [Arg('arg1[')]
    assert argstr == '{arg1[}'
    assert source[translator.pos] == '['
    assert translator.pos == 7


def test_extract_args_only_opt_unmatched():
    source = '[arg2{arg1}some text'
    translator = Translator(source)
    args, argstr = translator.extract_args()
    assert args == []
    assert argstr == ''
    assert source[translator.pos] == '['


def test_extract_args_min_args():
    source = '{arg1}[arg2]some text'
    translator = Translator(source)
    args, argstr = translator.extract_args(min_args=2)
    assert args == [Arg('arg1'), Arg('arg2', optional=True)]
    assert argstr == '{arg1}[arg2]'
    assert source[translator.pos] == 's'


def test_extract_args_min_args_missing():
    source = '{arg1}[arg2]some text'
    translator = Translator(source)
    with pytest.raises(TranslationError) as excinfo:
        translator.extract_args(min_args=3)
    assert 'Too few arguments' in excinfo.value.msg


def test_extract_args_max_args():
    source = '{arg1}  [arg2] {arg1}some text'
    translator = Translator(source)
    args, argstr = translator.extract_args(max_args=4)
    assert args == [Arg('arg1'), Arg('arg2', optional=True), Arg('arg1')]
    assert argstr == '{arg1}  [arg2] {arg1}'
    assert source[translator.pos] == 's'


def test_extract_args_max_args_less():
    source = '{arg1}  [arg2] {arg1}some text'
    translator = Translator(source)
    args, argstr = translator.extract_args(max_args=2)
    assert args == [Arg('arg1'), Arg('arg2', optional=True)]
    assert argstr == '{arg1}  [arg2]'
    assert source[translator.pos] == ' '


