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


def test_equation():
    source = dedent('''
    \\documentclass{article}
    \\document:
        Here is an equation:
        \\equation:
            f(x) = x^2
    ''')
    res = translate(source)
    assert res == dedent(
    '''
    \\documentclass{article}
    \\begin{document}
        Here is an equation:
        \\begin{equation}
            f(x) = x^2
        \\end{equation}
    \\end{document}
    ''')


def test_multiple_equations():
    source = dedent('''
    \\documentclass{article}
    \\document:
    Here is an equation:
    \\equation:
        f(x) = x^2
    Here is another equation:
    \\equation:
        f(x) = x^3
    Here are some concluding words.
    ''')
    # import pdb; pdb.set_trace()
    res = translate(source)
    assert res == dedent(
    '''
    \\documentclass{article}
    \\begin{document}
    Here is an equation:
    \\begin{equation}
        f(x) = x^2
    \\end{equation}
    Here is another equation:
    \\begin{equation}
        f(x) = x^3
    \\end{equation}
    Here are some concluding words.
    \\end{document}
    ''')


def test_multiple_nested_environments():
    source = dedent('''
    \\documentclass{article}
    \\document:
    Here is an equation:
    \\equation:
        \\split:
            f(x) = x^2
    Here is another equation:
    \\equation:
        \\split:
            f(x) = x^3
    Here are some concluding words.
    ''')
    # import pdb; pdb.set_trace()
    res = translate(source)
    assert res == dedent(
    '''
    \\documentclass{article}
    \\begin{document}
    Here is an equation:
    \\begin{equation}
        \\begin{split}
            f(x) = x^2
        \\end{split}
    \\end{equation}
    Here is another equation:
    \\begin{equation}
        \\begin{split}
            f(x) = x^3
        \\end{split}
    \\end{equation}
    Here are some concluding words.
    \\end{document}
    ''')


