from textwrap import dedent

import pytest

# from hltex.control import environments
from hltex.errors import DependencyError
from hltex.translator import translate


def test_pysplice():
    source = '\\pysplice:\n    print("3")'
    res = translate(source)
    assert res == "3\n"


def test_bad():
    source = '\n\\pysplice: prin("3")\n'
    with pytest.raises(DependencyError) as excinfo:
        translate(source)
    assert "Python execution failed" in excinfo.value.msg
    assert "NameError" in excinfo.value.msg


def test_generate_macros():
    source = "\n\\pysplice:\n    print('\\n'.join(['\\\\newcommand{\\cal%s}{\\mathcal{%s}}' % (c, c) for c in ['F', 'G', 'H', 'I', 'D', 'B']]))"
    res = translate(source)
    assert res == dedent(
        """
        \\newcommand{\\calF}{\\mathcal{F}}
        \\newcommand{\\calG}{\\mathcal{G}}
        \\newcommand{\\calH}{\\mathcal{H}}
        \\newcommand{\\calI}{\\mathcal{I}}
        \\newcommand{\\calD}{\\mathcal{D}}
        \\newcommand{\\calB}{\\mathcal{B}}
        """
    )


def test_file_env():
    source = dedent(
        """
        \\pysplice:
            with open('test.txt', 'r') as f:
                print(f.read())
        """
    )
    res = translate(source, file_env={"test.txt": "42"})
    assert res == dedent(
        """
        42
        """
    )


def test_nested_file_env():
    source = dedent(
        """
        \\pysplice:
            with open('folder/folder2/test.txt', 'r') as f:
                print(f.read())
        """
    )
    res = translate(source, file_env={"folder/folder2/test.txt": "42"})
    assert res == dedent(
        """
        42
        """
    )


def test_shared_python():
    source = dedent(
        """
        \\pysplice:
            x = 3
        \\pysplice:
            print(x)
        """
    )
    res = translate(source)
    assert res == dedent(
        """

        3
        """
    )
