from textwrap import dedent
from hltex.translator import Translator

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


