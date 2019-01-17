from textwrap import dedent

from hltex.newtranslator import translate


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
        \\end{document}
        """
    )
