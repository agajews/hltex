from ..errors import TranslationError


class Arg:
    def __init__(self, contents, optional=False):
        self.contents = contents
        self.optional = optional

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def resolve_args(name, params, args):
    """
    params: a string consisting of `!`s and `?`s, where `!`s represent required arguments
        and `!`s represent optional arguments
    args: a list of `Arg`s to be resolved with the `params` string
    errors: if there is a missing required argument or a superfluous optional argument
    returns: a list of `Arg`s with additional `None`s for missing optional arguments
    raises: Exception if passed more args than params
    """
    all_args = []
    arg_num = 0
    if len(args) > len(params):
        raise TranslationError(
            "Too many arguments while resolving arguments for {}".format(name)
        )
    for param in params:
        if param == "!":
            if arg_num < len(args) and not args[arg_num].optional:
                all_args.append(args[arg_num].contents)
                arg_num += 1
            elif arg_num >= len(args):
                raise TranslationError(
                    "Missing required argument for command `{}`".format(name)
                )
            else:
                raise TranslationError(
                    "Superfluous optional argument provided to command `{}`".format(
                        name
                    )
                )
        else:
            if arg_num < len(args) and args[arg_num].optional:
                all_args.append(args[arg_num].contents)
                arg_num += 1
            else:
                all_args.append(None)
    return all_args


def unresolve_args(args):
    argstr = ""
    for arg in args:
        if arg is not None and arg.contents is not None:
            argstr += "[%s]" % arg.contents if arg.optional else "{%s}" % arg.contents
    return argstr


class Command:
    def __init__(self, name, translate_fn, params="", is_raw=False):
        self.name = name
        self.translate_fn = translate_fn
        self.params = params
        self.is_raw = is_raw
        assert all([p in "!?" for p in params])

    def translate(self, translator, args):
        return self.translate_fn(
            translator, *resolve_args(self.name, self.params, args)
        )


class Environment:
    def __init__(self, name, translate_fn, params="", is_raw=False):
        self.name = name
        self.translate_fn = translate_fn
        self.params = params
        self.is_raw = is_raw
        assert all([p in "!?" for p in params])

    def translate(self, translator, body, args):
        try:  # XXX: why?
            return self.translate_fn(
                translator, body, *resolve_args(self.name, self.params, args)
            )
        except TranslationError as e:
            raise e


def latex_cmd(name, *args):
    return "\\%s%s" % (name, unresolve_args(args))


def latex_env(name, before="", body="", after="", args="", post_env=""):
    return "\\begin{%s}%s%s%s%s\\end{%s}%s" % (
        name,
        args,
        before,
        body,
        after,
        name,
        post_env,
    )


def translate_docclass(_translator, opts, arg):
    return latex_cmd("documentclass", Arg(opts, optional=True), Arg(arg))


def translate_verb(_translator, body):
    return latex_cmd("verb", Arg(body))


commands = {
    "docclass": Command("docclass", translate_docclass, params="?!"),
    "verb": Command("verb", translate_verb, params="!", is_raw=True),
    "colon": Command("colon", lambda _: ":", params=""),
}


def translate_eq(_translator, body, label):
    before = ""
    if label is not None:
        before = "\\label{eq:%s}" % label
    return latex_env("equation", before=before, body=body)


def translate_verbatim(_translator, body):
    return latex_env("verbatim", body=body)


environments = {
    "eq": Environment("eq", translate_eq, params="?"),
    "verbatim": Environment("verbatim", translate_verbatim, is_raw=True),
}
