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
    \\end{document}\n''')


def test_hello_indented():
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


def test_double_document():
    source = dedent('''
    \\documentclass{article}
    \\document:
    Hello?
    \\document:
        Goodbye
    ''')
    res = translate(source)
    print(res)
    assert res == dedent(
    '''
    \\documentclass{article}
    \\begin{document}
    Hello?
    \\begin{document}
        Goodbye
    \\end{document}
    \\end{document}
    ''')


def test_indented_bad(capsys):
    source = '''
    \\documentclass{article}
    \\document:
    Hello?
    \\document:
        Goodbye
    '''
    res = translate(source)
    assert 'document as a whole must not be indented' in capsys.readouterr().err


