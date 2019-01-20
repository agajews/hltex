from ..pybox import Pybox, default_docker
from .control import Environment, environments


def translate_pysplice(state, body, docker):
    if docker is None:
        docker = default_docker
    if state.pyboxes.get(docker) is None:
        state.pyboxes[docker] = Pybox(docker=docker, file_env=state.file_env)
    return state.pyboxes[docker].run(body)


environments["pysplice"] = Environment(
    "pysplice", translate_pysplice, params="?", raw=True
)
