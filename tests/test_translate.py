from textwrap import dedent

from hltex.translator import translate


def test_translate():
    source = dedent(
        """
        \\documentclass{article}
        \\document:
            Hi!
        """
    )
    res = translate(source)
    print(repr(res))
    assert res == dedent(
        """
        \\documentclass{article}
        \\begin{document}
            Hi!
        \\end{document}"""
    )


def test_preamble():
    source = dedent(
        """
        \\documentclass{article}
        ===
        Hi!
        """
    )
    res = translate(source)
    print(repr(res))
    assert res == dedent(
        """
        \\documentclass{article}
        \\begin{document}
        Hi!
        \\end{document}"""
    )


def test_no_newline():
    source = dedent(
        """
        \\documentclass{article}
        ===
        Hi!"""
    )
    res = translate(source)
    print(repr(res))
    assert res == dedent(
        """
        \\documentclass{article}
        \\begin{document}
        Hi!
        \\end{document}"""
    )


def test_no_beginning_newline():
    source = "\\documentclass{article}\n===\nHi!"
    res = translate(source)
    print(repr(res))
    assert res == dedent(
        "\\documentclass{article}\n\\begin{document}\nHi!\n\\end{document}"
    )


def test_translate_spacing():
    source = dedent(
        """
        \\documentclass{article}
        ===
        \\equation:
            f(x) = 3x

        \\equation:
            g(x) = 4x
        """
    )
    res = translate(source)
    print(res)
    print(repr(res))
    assert res == dedent(
        """
        \\documentclass{article}
        \\begin{document}
        \\begin{equation}
            f(x) = 3x
        \\end{equation}

        \\begin{equation}
            g(x) = 4x
        \\end{equation}
        \\end{document}"""
    )
