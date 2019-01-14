from .context import increment, parse_while
from .errors import InvalidIndentation


def iswhitespace(char):
    return str.isspace(char) and not char == "\n"


def parse_empty(state):
    """
    precondition: `state.pos` is at the start of a line
    postcondition: `state.pos` is at the start of the next non-whitespace line (i.e.
        after the preceeding newline), or at `len(state.text)` if there isn't a
        next non-whitespace line
    """
    start = state.pos
    body = state.run(parse_while, pred=iswhitespace)
    if state.finished():
        return body
    if state.text[state.pos] == "\n":
        state.run(increment)
        return body + "\n", parse_empty
    state.pos = start
    return body


def validate_indent_str(indent):
    """
    indent: str
    raises: InvalidIndentation if `indent` is nonempty and isn't either all tabs or all spaces
    """
    if not (all(s == " " for s in indent) or all(s == "\t" for s in indent)):
        raise InvalidIndentation("Indentation must be all spaces or all tabs")


def validate_indent(state, indent):
    """
    indent: str
    precondition: `state.indent_str` is not None
    raises: InvalidIndentation if `indent` is nonempty and isn't either all tabs or all spaces,
        or if `indent` isn't a multiple of `state.indent_str`, or if `indent` doesn't
        use the same indentation character as indent_str
    """
    validate_indent_str(indent)
    if not len(indent) % len(state.indent_str) == 0:
        raise InvalidIndentation(
            "Indentation must be in multiples of the base indentation {}".format(
                repr(state.indent_str)
            )
        )


def level_of_indent(state, indent):
    """
    indent: str
    precondition: `state.indent_str` is not None

    returns: the whole number of non-overlapping `state.indent_str` in `indent`
        (i.e. the indentation level where `state.indent_str` is the base unit of indentation)
    """
    return len(indent) // len(state.indent_str)


def get_indent(state):
    """
    precondition: `self.pos` is at the start of a line
    postcondition: `self.pos` is where it started
    returns: the indentation string of the current line
    """
    start = state.pos
    indent = state.run(parse_while, pred=iswhitespace)
    state.pos = start
    return indent


def calc_indent_level(state):
    """
    precondition: `self.pos` is at the start of a line
    postcondition: `self.pos` is where it started
    errors: if the current line isn't well-indented (e.g. if the indentation contains
        both tabs and spaces)
    returns: the indentation level of the current line, in terms of `self.indent_str` units
    """
    indent = state.run(get_indent)
    if state.indent_str is None:
        validate_indent_str(indent)
        state.indent_str = indent
    validate_indent(state, indent)
    return level_of_indent(state, indent)
