from textwrap import dedent, indent

from .context import increment, parse_until, parse_while
from .errors import (
    InternalError,
    InvalidSyntax,
    MissingArgument,
    UnexpectedEOF,
    UnexpectedIndentation,
)
from .indentation import calc_indent_level, iswhitespace, parse_empty
from .newcontrol import latex_env


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
        if param.optional:
            arg = state.run(parse_optional_arg)
        else:
            arg = state.run(parse_required_arg, name=name)
        args.append(arg)
    return args


def parse_optional_argstr(state):
    """
    precondition: `state.pos` is somewhere an optional argstr (typically would be called
        from the first character following the opening bracket)
    postcondition: `state.pos` is at the first character following the closing brace
    """
    body = state.run(parse_until, pred=lambda c: c in "\n{}\\]")
    if state.finished() or state.text[state.pos] == "\n":
        return None
    if state.text[state.pos] == "{":
        state.run(increment)
        body += "{" + state.run(parse_group, end="}") + "}"
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
        body += "[" + state.run(parse_optional_argstr) + "]"
        return body, parse_argstr
    raise InternalError()


def parse_custom_command(state, command):
    """
    precondition: `state.pos` is at the first character following the name of a custom
        command
    postcondition: `state.pos` is at the first character following the last argument's
        closing bracket or brace
    """
    args = state.run(parse_args, name=command.name, params=command.params)
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
    return indent(
        state.indent_str * outer_indent_level,
        latex_env(state, name, dedent(body), argstr),
    )


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
    state.run(increment)
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
    state.run(parse_while, pred=iswhitespace)
    if state.finished():
        raise UnexpectedEOF("Environment missing body")
    if not state.text[state.pos] == "\n":  # TODO: parse one-liners better
        return state.run(parse_until, lambda c: c == "\n")
    state.run(increment)
    body = state.run(parse_empty)
    indent_level = calc_indent_level(state)
    if indent_level != outer_indent_level + 1:
        raise InvalidSyntax("Missing indentation after environment")
    return body, parse_block


def parse_block_newline(state, outer_indent_level):
    """
    precondition: `state.pos` is at a newline in a block
    postcondition: `state.pos` is at the stat of the next line
    """
    state.run(increment)
    if state.finished():
        return "\n"
    indent_level = calc_indent_level(state)
    if indent_level < outer_indent_level:
        return "\n"
    if indent_level > outer_indent_level:
        raise UnexpectedIndentation("Indentation should only follow environments")
    return "\n", parse_block  # triggers the next parse_block command


def parse_block_control(state, outer_indent_level):
    """
    precondition: `state.pos` is at a backslash in a block
    postcondition: `state.pos` is either at the first character following the last
        argument's closing brace, or at the start of the next non-empty line for
        indented environments, or at the start of the next line for one-liners
    """
    name = state.run(parse_control_name)
    if name in state.commands:
        return state.run(parse_custom_command, command=state.commands[name])
    if name in state.environments:
        return state.run(
            parse_custom_environment,
            environment=state.environments[name],
            outer_indent_level=outer_indent_level,
        )
    return state.run(
        parse_native_control, name=name, outer_indent_level=outer_indent_level
    )


def parse_block(state):
    """
    precondition: `state.pos` is somewhere in the block (typically `parse_block` should
        be called from the start of the line (e.g. the line after a colon))
    postcondition: `state.pos` is at the start of the next non-empty line after the
        indented block
    """
    outer_indent_level = calc_indent_level(state)
    body = state.run(parse_until, pred=lambda c: c in "\\\n{}")

    if state.finished():
        return body
    if state.text[state.pos] == "\n":
        return body, parse_block_newline, {"outer_indent_level": outer_indent_level}
    if state.text[state.pos] == "\\":
        return body, parse_block_control, {"outer_indent_level": outer_indent_level}
    if state.text[state.pos] == "{":
        body += "{" + state.run(parse_group, end="}") + "}"
        return body, parse_block
    if state.text[state.pos] == "}":
        raise InvalidSyntax("Unexpected `}`")
    raise InternalError()
