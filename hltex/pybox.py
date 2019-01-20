import json
from textwrap import dedent

from .errors import DependencyError

default_docker = "czentye/matplotlib-minimal"


class Pybox:
    def __init__(self, file_env=None, docker=None, cputime=10, memory=64):
        if file_env is None:
            file_env = {}
        if docker is None:
            docker = default_docker
        self.docker = docker
        files = [
            {
                "name": "main.py",
                "content": dedent(
                    """
            import json as __json
            import io as __io
            from textwrap import indent as __indent
            from contextlib import redirect_stdout as __redirect_stdout


            if __name__ == '__main__':
                while True:
                    __code = input()
                    __request = eval(__code)
                    if __request is None:
                        break
                    __string = None
                    try:
                        __string = __io.StringIO()
                        with __redirect_stdout(__string):
                            exec(__request)
                        __res = {'output': __string.getvalue(), 'error': None}
                    except Exception as e:
                        __res = {'output': __string.getvalue(), 'error': type(e).__name__ + ': ' + str(e)}
                    print(__json.dumps(__res))
            """
                ).encode("utf-8"),
            }
        ]

        for name, content in file_env.items():
            files.append({"name": name, "content": content.encode("utf-8")})

        limits = {"cputime": cputime, "memory": memory}

        try:
            import hlbox

            hlbox.configure(profiles=[hlbox.Profile("python", docker)])
            self.sandbox = hlbox.create(
                "python",
                "python3 -u main.py",
                files=files,
                limits=limits,
                prep_download=True,
            )
        except Exception as e:
            raise DependencyError(
                "Failed to configure HLBox for pysplice. Make sure you have HLBox and Docker installed and configured.\n"
                + str(e)
            )

    def run(self, body):
        import hlbox

        result = hlbox.runline(self.sandbox, repr(body) + "\n")
        if result["exit_code"] != 0:
            raise DependencyError("Something went wrong executing this Python block")

        output = json.loads(result["stdout"].decode("utf-8"))
        if output["error"] is not None:
            raise DependencyError("Python execution failed: {}".format(output["error"]))
        return output["output"]
