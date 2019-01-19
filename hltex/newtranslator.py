from .context import increment, parse_until, parse_while
from .errors import (
    InternalError,
    InvalidSyntax,
    MissingArgument,
    UnexpectedEOF,
    UnexpectedIndentation,
)
from .indentation import (
    calc_indent_level,
    iswhitespace,
    line_is_empty,
    parse_empty,
    postprocess_block,
    preprocess_block,
)
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
    name = parse_while(state, pred=str.isalpha)
    if not name:
        name = increment(state)
    return name


def parse_arg_control(state):
    """
    precondition: `state.pos` is at the first character following a backslash
    postcondition: `state.pos` is either at the first character following the
    command name (for native commands) or at the first character following the last
    argument (for custom commands)
    """
    name = parse_control_name(state)
    if name in state.commands:
        return parse_custom_command(state, command=state.commands[name])
    return "\\" + name


def parse_comment(state):
    """
    precondition: `state.pos` is after a percent sign
    postcondition: `state.pos` is at the newline following the percent sign (or at the
        EOF if there is no following newline)
    """
    return "%" + parse_until(state, lambda c: c == "\n")


def parse_group(state, end):
    """
    precondition: `state.pos` is somewhere inside a group (typically would be called
        from the first character following the opening brace or bracket)
    postcondition: `state.pos` is at the first character following the closing brace or
        bracket
    """
    body = parse_until(state, pred=lambda c: c in "{}\\%" + end)
    if state.finished():
        raise UnexpectedEOF("Missing closing `{}`".format(end))
    if state.text[state.pos] == "{":
        increment(state)
        body += "{" + parse_group(state, end="}") + "}"
        return body + parse_group(state, end)
    if state.text[state.pos] == "\\":
        increment(state)
        body += parse_arg_control(state)
        return body + parse_group(state, end)
    if state.text[state.pos] == end:
        increment(state)
        return body
    if state.text[state.pos] == "%":
        increment(state)
        body += parse_comment(state)
        return body + parse_group(state, end)
    if state.text[state.pos] == "}":
        raise InvalidSyntax("Unexpected `}`")
    raise InternalError()


def parse_optional_arg(state):
    """
    precondition: `state.pos` is at the first character following the previous argument
    postcondition: `state.pos` is either at the first character following the closing
        bracket, or where it started if no closing bracket was found
    """
    start = state.pos
    parse_while(state, pred=iswhitespace)
    if state.finished() or not state.text[state.pos] == "[":
        state.pos = start
        return None
    increment(state)
    return parse_group(state, end="]")


def parse_required_arg(state, name):
    """
    precondition: `state.pos` is at the first character following the previous argument
    postcondition: `state.pos` is at the first character following the closing brace
    """
    parse_while(state, pred=iswhitespace)
    if state.finished():
        raise UnexpectedEOF("Missing required argument for `{}`".format(name))
    if not state.text[state.pos] == "{":
        raise MissingArgument("Missing required argument for `{}`".format(name))
    increment(state)
    return parse_group(state, end="}")


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
            arg = parse_optional_arg(state)
        elif param == "!":
            arg = parse_required_arg(state, name=name)
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
    start = state.pos
    body = parse_until(state, pred=lambda c: c in "\n{}\\[]%")
    if state.finished() or state.text[state.pos] in "\n%":
        return None
    if state.text[state.pos] == "]":
        increment(state)
        return body
    if state.text[state.pos] == "}":
        raise InvalidSyntax("Unexpected `}`")
    if state.text[state.pos] == "{":
        increment(state)
        body += "{" + parse_group(state, end="}") + "}"
    elif state.text[state.pos] == "[":
        increment(state)
        body += "[" + parse_group(state, end="]") + "]"
    elif state.text[state.pos] == "\\":
        increment(state)
        body += parse_arg_control(state)
    else:
        raise InternalError()
    res = parse_optional_argstr(state)
    if res is None:
        state.pos = start
        return None
    return body + res


def parse_argstr(state):
    """
    precondition: `state.pos` is at the first character following the name of a control
        sequence
    postcondition: `state.pos` is at the first character following the last argument's
        closing bracket or brace
    """
    start = state.pos
    body = parse_while(state, pred=iswhitespace)
    if state.finished() or state.text[state.pos] not in "{[":
        state.pos = start
        return ""
    if state.text[state.pos] == "{":
        increment(state)
        body += "{" + parse_group(state, end="}") + "}"
        return body + parse_argstr(state)
    if state.text[state.pos] == "[":
        increment(state)
        res = parse_optional_argstr(state)
        if res is None:
            state.pos = start
            return ""
        body += "[" + res + "]"
        return body + parse_argstr(state)
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
    argstr = parse_argstr(state)
    start = state.pos
    parse_while(state, pred=iswhitespace)
    if state.finished() or state.text[state.pos] != ":":
        state.pos = start
        return "\\" + name + argstr
    increment(state)
    body = parse_environment_body(state, outer_indent_level=outer_indent_level)
    res = latex_env(state, name, argstr, preprocess_block(body))
    # Don't indent the first line
    return postprocess_block(res, state, outer_indent_level)


def parse_custom_environment(state, environment, outer_indent_level):
    """
    precondition: `state.pos` is at the first character following the name of a custom
        environment
    postcondition: `state.pos` is at the start of the next non-empty line following the
        indented block
    """
    args = parse_args(state, name=environment.name, params=environment.params)
    parse_while(state, pred=iswhitespace)
    if state.finished():
        raise UnexpectedEOF("Environments must be followed by colons")
    if not state.text[state.pos] == ":":
        raise InvalidSyntax("Environments must be followed by colons")
    increment(state)
    body = parse_environment_body(state, outer_indent_level=outer_indent_level)
    res = environment.translate(state, preprocess_block(body), args)
    return postprocess_block(res, state, outer_indent_level)


def parse_oneliner(state, outer_indent_level):
    body = parse_until(state, pred=lambda c: c in "\\\n{}%")

    if state.finished():
        return body
    if state.text[state.pos] == "\n":
        increment(state)
        return body
    if state.text[state.pos] == "\\":
        increment(state)
        return body + parse_block_control(state, outer_indent_level=outer_indent_level)
    if state.text[state.pos] == "{":
        increment(state)
        body += "{" + parse_group(state, end="}") + "}"
        return body + parse_block_body(state, outer_indent_level=outer_indent_level)
    if state.text[state.pos] == "%":
        increment(state)
        body += parse_comment(state)
        return body + parse_block_body(state, outer_indent_level=outer_indent_level)
    if state.text[state.pos] == "}":
        raise InvalidSyntax("Unexpected `}`")
    raise InternalError()


def parse_environment_body(state, outer_indent_level):
    """
    precondition: `state.pos` is at the first character following the colon
    postcondition: `state.pos` is at the next non-empty line following the indented
        block, or at the end of the line for one-liners
    """
    parse_while(state, pred=iswhitespace)
    if state.finished():
        raise UnexpectedEOF("Environment missing body")
    if state.text[state.pos] not in "\n%":  # TODO: parse one-liners better
        # return parse_oneliner(state, outer_indent_level)
        res = parse_until(state, pred=lambda c: c == "\n")
        # increment(state)
        return res
    comment = None
    if state.text[state.pos] == "%":
        increment(state)
        comment = parse_comment(state)
    body = parse_empty(state)
    # increment(state)
    if line_is_empty(state):
        raise UnexpectedEOF("Environment missing body")
    indent_level = calc_indent_level(state)
    if indent_level != outer_indent_level + 1:
        raise InvalidSyntax("Missing indentation after environment")
    if comment is not None:
        indent = (state.indent_str or "") * indent_level
        body = "\n" + indent + comment + body
    return body + parse_block(state)


def parse_document(state):
    parse_while(state, pred=lambda c: c == "=")
    if state.finished():
        raise UnexpectedEOF("Missing document body")
    if state.text[state.pos] != "\n":
        raise InvalidSyntax("Missing newline after document delineator")
    increment(state)
    if calc_indent_level(state) != 0:
        raise UnexpectedIndentation("The document as a whole must not be indented")
    state.in_document = True
    document = "\n" + parse_block(state)
    return postprocess_block(
        latex_env(state, "document", "", preprocess_block(document)), state, 0
    )


def parse_block_newline(state, outer_indent_level, preamble=False):
    """
    precondition: `state.pos` is at a newline in a block
    postcondition: `state.pos` is at the start of the next line
    """
    start = state.pos
    increment(state)
    if preamble and state.text[state.pos : state.pos + 3] == "===":
        return "\n" + parse_document(state)
    if line_is_empty(state):
        return "\n" + parse_block_body(
            state, outer_indent_level=outer_indent_level, preamble=preamble
        )
    indent_level = calc_indent_level(state)
    if indent_level < outer_indent_level:
        state.pos = start
        return ""
    if indent_level > outer_indent_level:
        raise UnexpectedIndentation("Indentation should only follow environments")
    return "\n" + parse_block_body(
        state, outer_indent_level=outer_indent_level, preamble=preamble
    )


def parse_block_control(state, outer_indent_level, preamble=False):
    """
    precondition: `state.pos` is at a backslash in a block
    postcondition: `state.pos` is either at the first character following the last
        argument's closing brace, or at the start of the next non-empty line for
        indented environments, or at the start of the next line for one-liners
    """
    increment(state)
    name = parse_control_name(state)
    if name in state.commands:
        body = parse_custom_command(state, command=state.commands[name])
    if name in state.environments:
        body = parse_custom_environment(
            state,
            environment=state.environments[name],
            outer_indent_level=outer_indent_level,
        )
    else:
        body = parse_native_control(
            state, name=name, outer_indent_level=outer_indent_level
        )
    return body + parse_block_body(
        state, outer_indent_level=outer_indent_level, preamble=preamble
    )


def parse_block_body(state, outer_indent_level, preamble=False):
    """
    precondition: `state.pos` is somewhere inside a block
    postcondition: `state.pos` is at the start of the next non-empty line after the
        indented block, or at `len(state.text)` if there is no next non-empty line
    """
    body = parse_until(state, pred=lambda c: c in "\\\n{}%")

    if state.finished():
        return body
    if state.text[state.pos] == "\n":
        # body += "\n"
        # increment(state)
        return body + parse_block_newline(
            state, outer_indent_level=outer_indent_level, preamble=preamble
        )
    if state.text[state.pos] == "\\":
        # increment(state)
        return body + parse_block_control(
            state, outer_indent_level=outer_indent_level, preamble=preamble
        )
    if state.text[state.pos] == "{":
        increment(state)
        body += "{" + parse_group(state, end="}") + "}"
        return body + parse_block_body(
            state, outer_indent_level=outer_indent_level, preamble=preamble
        )
    if state.text[state.pos] == "%":
        increment(state)
        body += parse_comment(state)
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
    body = parse_empty(state)
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
    res = parse_block(state, preamble=True)
    return res


# TODO: raw blocks, arguments
# TODO: comments
