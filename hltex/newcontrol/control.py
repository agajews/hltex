from ..indentation import indent_body

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
    body = indent_body(body, state)
    return "\\begin{%s}%s%s\\end{%s}" % (name, argstr, body, name)
