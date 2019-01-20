from .control import Environment, environments, latex_env


def translate_eq(state, body, label):
    if label is not None:
        argstr = "\\label{eq:%s}" % label
    else:
        argstr = ""
    return latex_env(state, "equation", argstr, body)


environments["eq"] = Environment("eq", translate_eq, params="?", raw=True)
