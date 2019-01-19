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

    # def run(self, context, **kwargs):
    #     """
    #     context: a context function taking a state and optionally some kwargs, returning
    #     either a string (representing the result of the translation), or a tuple
    #     with either:
    #         just a string, the result of the translation
    #         a string and a next context function to run (or None to end)
    #         a string, a next context, and some kwargs to pass to the next context
    #     """
    #     string = ""
    #     start = self.pos
    #     assert self.pos <= len(self.text)
    #     while context is not None:
    #         assert self.pos <= len(self.text)
    #         res = context(self, **kwargs)
    #         if res is None:
    #             self.pos = start
    #             return None
    #         if isinstance(res, tuple):  # TODO: clean up this logic
    #             assert 1 <= len(res) <= 3
    #             string += res[0]
    #             if len(res) > 1:
    #                 context = res[1]
    #             else:
    #                 context = None
    #             if len(res) > 2:
    #                 kwargs = res[2]
    #             else:
    #                 kwargs = {}
    #         else:
    #             assert isinstance(string, str)
    #             string += res
    #             context = None
    #             kwargs = {}
    #     return string

    def finished(self):
        return self.pos >= len(self.text)
