from textwrap import dedent, indent

from .context import increment, parse_until, parse_while
from .errors import (
    InternalError,
    InvalidSyntax,
    MissingArgument,
    UnexpectedEOF,
    UnexpectedIndentation,
)
from .indentation import calc_indent_level, iswhitespace, line_is_empty, parse_empty
from .newcontrol import latex_env
from .state import State


def parse_control_name(state):
    """
    precondition: `state.pos` is at the first character following a backslash
    postcondition: `state.pos` is at the first character following the name of the
        control sequence
    raises: UnexpectedEOF if there is no character following the name of the control
        sequence
    """
    if state.finished():
        raise UnexpectedEOF(
            "Unescaped backslashes must be followed by at least one character"
        )
    name = state.run(parse_while, pred=str.isalpha)
    if not name:
        name = state.run(increment)
    return name


def parse_arg_control(state):
    """
    precondition: `state.pos` is at the first character following a backslash
    postcondition: `state.pos` is either at the first character following the
    command name (for native commands) or at the first character following the last
    argument (for custom commands)
    """
    name = state.run(parse_control_name)
    if name in state.commands:
        return state.run(parse_custom_command, command=state.commands[name])
    return "\\" + name


def parse_group(state, end):
    """
    precondition: `state.pos` is somewhere inside a group (typically would be called
        from the first character following the opening brace or bracket)
    postcondition: `state.pos` is at the first character following the closing brace or
        bracket
    """
    start = state.pos
    body = state.run(parse_until, pred=lambda c: c in "{}\\" + end)
    if state.finished():
        raise UnexpectedEOF("Missing closing `{}`".format(end))
    if state.text[state.pos] == "{":
        state.run(increment)
        body += "{" + state.run(parse_group, end="}") + "}"
        return body, parse_group, {"end": end}
    if state.text[state.pos] == "\\":
        state.run(increment)
        body += state.run(parse_arg_control)
        return body, parse_group, {"end": end}
    if state.text[state.pos] == end:
        state.run(increment)
        return body
    if state.text[state.pos] == "}":
        raise InvalidSyntax("Unexpected `}`")
    raise InternalError()


def parse_optional_arg(state):
    """
    precondition: `state.pos` is at the first character following the previous argument
    postcondition: `state.pos` is either at the first character following the closing
        bracket, or where it started if no closing bracket was found
    """
    state.run(parse_while, pred=iswhitespace)
    if state.finished() or not state.text[state.pos] == "[":
        return None
    state.run(increment)
    return state.run(parse_group, end="]")


def parse_required_arg(state, name):
    """
    precondition: `state.pos` is at the first character following the previous argument
    postcondition: `state.pos` is at the first character following the closing brace
    """
    state.run(parse_while, pred=iswhitespace)
    if state.finished():
        raise UnexpectedEOF("Missing required argument for `{}`".format(name))
    if not state.text[state.pos] == "{":
        raise MissingArgument("Missing required argument for `{}`".format(name))
    state.run(increment)
    return state.run(parse_group, end="}")


def parse_args(state, name, params):
    """
    precondition: `state.pos` is at the first character following the name of a control
        sequence
    postcondition: `state.pos` is at the first character following the last argument's
        closing bracket or brace
    """
    args = []
    for param in params:
        if param == "?":
            arg = state.run(parse_optional_arg)
        elif param == "!":
            arg = state.run(parse_required_arg, name=name)
        else:
            raise InternalError()
        args.append(arg)
    return args


def parse_optional_argstr(state):
    """
    precondition: `state.pos` is somewhere an optional argstr (typically would be called
        from the first character following the opening bracket)
    postcondition: `state.pos` is at the first character following the closing brace
    """
    body = state.run(parse_until, pred=lambda c: c in "\n{}\\[]")
    if state.finished() or state.text[state.pos] == "\n":
        return None
    if state.text[state.pos] == "{":
        state.run(increment)
        body += "{" + state.run(parse_group, end="}") + "}"
        return body, parse_optional_argstr
    if state.text[state.pos] == "[":
        state.run(increment)
        body += "[" + state.run(parse_group, end="]") + "]"
        return body, parse_optional_argstr
    if state.text[state.pos] == "\\":
        state.run(increment)
        body += state.run(parse_arg_control)
        return body, parse_optional_argstr
    if state.text[state.pos] == "]":
        state.run(increment)
        return body
    if state.text[state.pos] == "}":
        raise InvalidSyntax("Unexpected `}`")
    raise InternalError()


def parse_argstr(state):
    """
    precondition: `state.pos` is at the first character following the name of a control
        sequence
    postcondition: `state.pos` is at the first character following the last argument's
        closing bracket or brace
    """
    start = state.pos
    body = state.run(parse_while, pred=iswhitespace)
    if state.finished() or state.text[state.pos] not in "{[":
        state.pos = start
        return ""
    if state.text[state.pos] == "{":
        state.run(increment)
        body += "{" + state.run(parse_group, end="}") + "}"
        return body, parse_argstr
    if state.text[state.pos] == "[":
        state.run(increment)
        res = state.run(parse_optional_argstr)
        if res is None:
            state.pos = start
            return ""
        body += "[" + res + "]"
        return body, parse_argstr
    raise InternalError()


def parse_custom_command(state, command):
    """
    precondition: `state.pos` is at the first character following the name of a custom
        command
    postcondition: `state.pos` is at the first character following the last argument's
        closing bracket or brace
    """
    args = parse_args(state, name=command.name, params=command.params)
    return command.translate(state, args)


def parse_native_control(state, name, outer_indent_level):
    """
    precondition: `state.pos` is at the first character following the name of a
        native control sequence
    postcondition: `state.pos` is at the first character following either the last
        argument's closing bracket or brace for commands, or at the start of the next
        non-empty block after the indented block
    """
    argstr = state.run(parse_argstr)
    start = state.pos
    state.run(parse_while, pred=iswhitespace)
    if state.finished() or state.text[state.pos] != ":":
        state.pos = start
        return "\\" + name + argstr
    state.run(increment)
    body = state.run(parse_environment_body, outer_indent_level=outer_indent_level)
    res = latex_env(state, name, argstr, dedent(body))
    # Don't indent the first line
    lines = res.split("\n")
    assert lines
    res = lines[0]
    if len(lines) > 1:
        res += "\n" + indent(
            "\n".join(lines[1:]), (state.indent_str or "") * outer_indent_level
        )
    return res


def parse_custom_environment(state, environment, outer_indent_level):
    """
    precondition: `state.pos` is at the first character following the name of a custom
        environment
    postcondition: `state.pos` is at the start of the next non-empty line following the
        indented block
    """
    args = state.run(parse_args, name=environment.name, params=environment.params)
    state.run(parse_while, pred=iswhitespace)
    if state.finished():
        raise UnexpectedEOF("Environments must be followed by colons")
    if not state.text[state.pos] == ":":
        raise InvalidSyntax("Environments must be followed by colons")
    # state.run(increment)
    body = state.run(parse_environment_body, outer_indent_level=outer_indent_level)
    return indent(
        state.indent_str * outer_indent_level,
        environment.translate(state, args, dedent(body)),
    )


def parse_environment_body(state, outer_indent_level):
    """
    precondition: `state.pos` is at the first character following the colon
    postcondition: `state.pos` is at the next non-empty line following the indented
        block, or at the end of the line for one-liners
    """
    print(repr(state.text[state.pos :]))
    state.run(parse_while, pred=iswhitespace)
    if state.finished():
        raise UnexpectedEOF("Environment missing body")
    if not state.text[state.pos] == "\n":  # TODO: parse one-liners better
        res = state.run(parse_until, pred=lambda c: c == "\n")
        increment(state)
        return res
    # state.run(increment)
    body = state.run(parse_empty)
    if line_is_empty(state):
        raise UnexpectedEOF("Environment missing body")
    indent_level = calc_indent_level(state)
    print(indent_level)
    print(state.indent_str)
    if indent_level != outer_indent_level + 1:
        raise InvalidSyntax("Missing indentation after environment")
    return body, parse_block


def parse_document(state):
    state.run(parse_while, pred=lambda c: c == "=")
    if state.finished():
        raise UnexpectedEOF("Missing document body")
    if state.text[state.pos] != "\n":
        raise InvalidSyntax("Missing newline after document delineator")
    state.run(increment)
    if calc_indent_level(state) != 0:
        raise UnexpectedIndentation("The document as a whole must not be indented")
    state.in_document = True
    document = state.run(parse_block)
    return latex_env(state, "document", "", "\n" + document)


def parse_block_newline(state, outer_indent_level, preamble=False):
    """
    precondition: `state.pos` is at a newline in a block
    postcondition: `state.pos` is at the start of the next line
    """
    if preamble and state.text[state.pos : state.pos + 3] == "===":
        return parse_document(state)
    if line_is_empty(state):
        return parse_block_body(
            state, outer_indent_level=outer_indent_level, preamble=preamble
        )
    indent_level = calc_indent_level(state)
    if indent_level < outer_indent_level:
        return ""
    if indent_level > outer_indent_level:
        raise UnexpectedIndentation("Indentation should only follow environments")
    return parse_block_body(
        state, outer_indent_level=outer_indent_level, preamble=preamble
    )


def parse_block_control(state, outer_indent_level, preamble=False):
    """
    precondition: `state.pos` is at a backslash in a block
    postcondition: `state.pos` is either at the first character following the last
        argument's closing brace, or at the start of the next non-empty line for
        indented environments, or at the start of the next line for one-liners
    """
    print("Block control:", preamble)
    is_env = False
    name = state.run(parse_control_name)
    print("Got name", name)
    if name in state.commands:
        body = state.run(parse_custom_command, command=state.commands[name])
    if name in state.environments:
        is_env = True
        body = state.run(
            parse_custom_environment,
            environment=state.environments[name],
            outer_indent_level=outer_indent_level,
        )
    else:
        body = state.run(
            parse_native_control, name=name, outer_indent_level=outer_indent_level
        )
        if body and body[-1] == "\n":
            is_env = True
            print("Is env")
            print("At:", repr(state.text[state.pos :]))
            print(preamble)
    if is_env:
        return body + parse_block_newline(
            state, outer_indent_level=outer_indent_level, preamble=preamble
        )
    print("Going back to body")
    return body + parse_block_body(
        state, outer_indent_level=outer_indent_level, preamble=preamble
    )


def parse_block_body(state, outer_indent_level, preamble=False):
    """
    precondition: `state.pos` is somewhere inside a block
    postcondition: `state.pos` is at the start of the next non-empty line after the
        indented block, or at `len(state.text)` if there is no next non-empty line
    """
    body = state.run(parse_until, pred=lambda c: c in "\\\n{}")
    print("Body preamble", preamble)

    if state.finished():
        return body
    if state.text[state.pos] == "\n":
        body += "\n"
        state.run(increment)
        return body + parse_block_newline(
            state, outer_indent_level=outer_indent_level, preamble=preamble
        )
    if state.text[state.pos] == "\\":
        state.run(increment)
        return body + parse_block_control(
            state, outer_indent_level=outer_indent_level, preamble=preamble
        )
    if state.text[state.pos] == "{":
        state.run(increment)
        body += "{" + parse_group(state, end="}") + "}"
        return body + parse_block_body(
            state, outer_indent_level=outer_indent_level, preamble=preamble
        )
    if state.text[state.pos] == "}":
        raise InvalidSyntax("Unexpected `}`")
    raise InternalError()


def parse_block(state, preamble=False):
    """
    precondition: `state.pos` is at the start of a line in the block (typically
        `parse_block` should be called from the line after a colon)
    postcondition: `state.pos` is at the start of the next non-empty line after the
        indented block
    """
    body = state.run(parse_empty)
    if line_is_empty(state):
        return body
    if preamble and state.text[state.pos : state.pos + 3] == "===":
        return body + parse_document(state)
    outer_indent_level = calc_indent_level(state)
    return body + parse_block_body(
        state, outer_indent_level=outer_indent_level, preamble=preamble
    )


def translate(source):
    state = State(source)
    res = state.run(parse_block)
    return res


# TODO: raw blocks, arguments
# TODO: comments
# TODO: remove state.run pattern
