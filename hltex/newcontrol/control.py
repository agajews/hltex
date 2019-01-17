from textwrap import indent

commands = {}
environments = {}


class Command:
    def __init__(self, name, translate_fn, params=""):
        self.name = name
        self.translate_fn = translate_fn
        self.params = params
        assert all([p in "!?" for p in params])

    def translate(self, state, args):
        return self.translate_fn(state, *args)


class Environment:
    def __init__(self, name, translate_fn, params=""):
        self.name = name
        self.translate_fn = translate_fn
        self.params = params
        assert all([p in "!?" for p in params])

    def translate(self, state, body, args):
        return self.translate_fn(state, body, *args)


def latex_env(state, name, argstr, body):
    print(repr(body))
    assert body
    if body[0] == "\n":
        assert state.indent_str is not None
        body = indent(body, state.indent_str)
        print(repr(body))
    if body[-1] != "\n":
        body += "\n"
    return "\\begin{%s}%s%s\\end{%s}" % (name, argstr, body, name)