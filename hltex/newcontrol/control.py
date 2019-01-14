from textwrap import indent

commands = {}
environments = {}


def latex_env(state, name, argstr, body):
    return "\\begin{%s}%s\n%s\n\\end{%s}" % (
        name,
        argstr,
        indent(state.indent_str, body),
        name,
    )
