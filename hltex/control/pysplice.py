import json
from textwrap import dedent

from ..errors import TranslationError
from .control import Environment, environments


def translate_pysplice(translator, body):
    """
    Executes the body as a python snippet using epicbox
    """
    import hlbox

    if translator.sandbox is None:
        try:
            hlbox.configure(
                profiles=[hlbox.Profile("python", "czentye/matplotlib-minimal")]
            )

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

            for name, content in translator.file_env.items():
                files.append({"name": name, "content": content.encode("utf-8")})

            limits = {"cputime": 10, "memory": 64}
            translator.sandbox = hlbox.create(
                "python",
                "python3 -u main.py",
                files=files,
                limits=limits,
                prep_download=True,
            )

        except Exception as e:
            raise TranslationError(
                "Failed to configure HLBox for pysplice. Make sure you have HLBox and Docker installed and configured.\n"
                + str(e)
            )

    body = dedent(body).encode("utf-8")
    # print('Running line...')
    result = hlbox.runline(translator.sandbox, repr(body) + "\n")
    # print('Got ', result)
    # result = hlbox.run('python', 'python3 main.py', files=files, limits=limits, download_target=tmp_dir)

    if result["exit_code"] != 0:
        # err_msg = "Pysplice execution failed.\nCode block:\n{}\n\nOutput:\n{}".format(body, str(result))
        # err_lines = result['stderr'].decode('utf-8').split('\n')
        # err = err_lines[-2] if len(err_lines) else ''
        err_msg = "Pysplice execution failed"
        raise TranslationError(err_msg)

    output = json.loads(result["stdout"].decode("utf-8"))
    if output["error"] is not None:
        raise TranslationError("Pysplice execution failed: {}".format(output["error"]))
    return output["output"]


environments["pysplice"] = Environment("pysplice", translate_pysplice, is_raw=True)
