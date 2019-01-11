from textwrap import dedent

import pytest

from hltex.control import environments
from hltex.errors import TranslationError
from hltex.translator import Translator


def prep_translator(source, indent_level=0):
    translator = Translator(source)
    translator.indent_str = "    "
    translator.indent_level = indent_level
    return translator


def test_parse_block_pysplice():
    source = '    \\pysplice:\n        print("3")\nother text'
    translator = prep_translator(source)
    res = translator.parse_block()
    assert res == "    3\n"


def test_do_environment_pysplice():
    source = '\nprint("3")\n'
    translator = prep_translator(source, -1)
    assert translator.do_environment(environments["pysplice"], [], "", 0) == "3\n"


def test_do_environment_pysplice_bad():
    source = '\nprin("3")\n'
    translator = prep_translator(source, -1)
    with pytest.raises(TranslationError) as excinfo:
        translator.do_environment(environments["pysplice"], [], "", 0)
    assert "Pysplice execution failed" in excinfo.value.msg
    assert "NameError" in excinfo.value.msg


def test_pysplice_generate_macros():
    source = "\n\\pysplice:\n    print('\\n'.join(['\\\\newcommand{\\cal%s}{\\mathcal{%s}}' % (c, c) for c in ['F', 'G', 'H', 'I', 'D', 'B']]))"
    translator = prep_translator(source, -1)
    res = translator.parse_block()
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


def test_pysplice_file_env():
    source = dedent(
        """
    \\pysplice:
        with open('test.txt', 'r') as f:
            print(f.read())
    """
    )
    translator = Translator(source, {"test.txt": "42"})
    translator.indent_str = "    "
    translator.indent_level = -1
    res = translator.parse_block()
    assert res == dedent(
        """
    42

    """
    )


def test_pysplice_nested_file_env():
    source = dedent(
        """
    \\pysplice:
        with open('folder/folder2/test.txt', 'r') as f:
            print(f.read())
    """
    )
    translator = Translator(source, {"folder/folder2/test.txt": "42"})
    translator.indent_str = "    "
    translator.indent_level = -1
    res = translator.parse_block()
    assert res == dedent(
        """
    42

    """
    )


def test_pysplice_shared_python():
    source = dedent(
        """
    \\pysplice:
        x = 3
    \\pysplice:
        print(x)
    """
    )
    translator = prep_translator(source, -1)
    res = translator.parse_block()
    assert res == dedent(
        """

    3

    """
    )
