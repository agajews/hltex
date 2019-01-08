from textwrap import dedent
from hltex.translator import Translator


def translate(source):
    translator = Translator(source)
    return translator.translate()


def test_hello():
    source = dedent('''
    \\documentclass{article}
    ===
    Hello?
    ''')
    assert translate(source) == dedent(
    '''
    \\documentclass{article}
    \\begin{document}
    Hello?
    \\end{document}\n''')


def test_hello_comments():
    source = dedent('''
    \\documentclass{arti%???
    cle}
    ===
    Hello?
    %bye
    ''')
    assert translate(source) == dedent(
    '''
    \\documentclass{arti%???
    cle}
    \\begin{document}
    Hello?
    %bye
    \\end{document}\n''')


def test_hello_pysplice():
    source = dedent('''
    \\documentclass{article}
    ===
    Hello?
    \\pysplice:
        h = "hello"
        if True:
            print(h)
        y = "\\this should be ignored%this TOO"
        #_plz
        #\\this too:
        #%wut is dis

            #weird indentation too


    Bye
    ''')
    res = translate(source)
    print(res)
    assert res == dedent(
    '''
    \\documentclass{article}
    \\begin{document}
    Hello?
    hello
    Bye
    \\end{document}\n''')


def test_no_starting_newline():
    source = '\\documentclass{article}\n===\nHello?'
    assert translate(source) == '\\documentclass{article}\n\\begin{document}\nHello?\n\\end{document}\n'



# def test_double_document_mark():
#     source = dedent('''
#     \\documentclass{article}
#     ===
#     Hello?
#     ===
#         Goodbye
#     ''')
#     res = translate(source)
#     print(res)
#     assert res == dedent(
#     '''
#     \\documentclass{article}
#     \\begin{document}
#     Hello?
#     ===
#         Goodbye
#     \\end{document}
#     ''')


def test_indented_bad(capsys):
    source = '''
    \\documentclass{article}
    ===
        Hello?
    '''
    res = translate(source)
    assert 'document as a whole must not be indented' in capsys.readouterr().err


def test_equation():
    source = dedent('''
    \\documentclass{article}
    ===
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
    ===
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
    ===
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


def test_multiple_nested_environments():
    source = dedent('''
    ===
    The document environment is the only one which doesn't need to be indented.
    \\section{Some Words}
    Here are some words that are in this section.
    Math is fun, so here's an equation:
    \\eq:
        f(x) = x^2 + 3
    We might want to give our equation a label, like this:
    \\eq[cubic]:
        f(x) = x^3 - 4x^2 + 2
    We can reference our equation with Equation \\ref{eq:cubic}.
    This is automatically joined with the non-breaking space \\verb{~}.
    ''')
    # import pdb; pdb.set_trace()
    res = translate(source)
    print(res)
    assert res == dedent(
    '''
    \\begin{document}
    The document environment is the only one which doesn't need to be indented.
    \\section{Some Words}
    Here are some words that are in this section.
    Math is fun, so here's an equation:
    \\begin{equation}
        f(x) = x^2 + 3
    \\end{equation}
    We might want to give our equation a label, like this:
    \\begin{equation}\\label{eq:cubic}
        f(x) = x^3 - 4x^2 + 2
    \\end{equation}
    We can reference our equation with Equation \\ref{eq:cubic}.
    This is automatically joined with the non-breaking space \\verb{~}.
    \\end{document}
    ''')


def test_docclass():
    source = dedent('''
    \\docclass{article}
    ===
    Hello?
    ''')
    assert translate(source) == dedent(
    '''
    \\documentclass{article}
    \\begin{document}
    Hello?
    \\end{document}\n''')


def test_docclass_options():
    source = dedent('''
    \\docclass[twocolumn,twoside]{article}
    ===
    Hello?
    ''')
    assert translate(source) == dedent(
    '''
    \\documentclass[twocolumn,twoside]{article}
    \\begin{document}
    Hello?
    \\end{document}\n''')



def test_docclass_with_normal_latex_begin_end():
    source = dedent('''
    \\docclass{article}
    ===
    \\begin{document}
    Hello!
    \\end{document}
    ''')
    assert translate(source) == dedent(
    '''
    \\documentclass{article}
    \\begin{document}
    \\begin{document}
    Hello!
    \\end{document}
    \\end{document}
    ''')



