from .newcontrol import commands, environments


class State:
    def __init__(self, text, pos=0, indent_str=None):
        self.text = text
        self.pos = pos
        self.indent_str = indent_str
        self.commands = commands.copy()
        self.environments = environments.copy()

    def run(self, context, **kwargs):
        return context(self, **kwargs)

    def finished(self):
        return self.pos >= len(self.text)
