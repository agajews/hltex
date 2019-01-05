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
    \\end{document}
    ''')
