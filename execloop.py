import json as __json
import io as __io
from textwrap import indent as __indent
from contextlib import redirect_stdout as __redirect_stdout


if __name__ == '__main__':
    while True:
        __code = input()
        __string = None
        try:
            # f_code = 'def f():\n' + indent(eval(code), '    ')
            __string = __io.StringIO()
            with __redirect_stdout(__string):
                exec(eval(__code))
            __res = {'output': __string.getvalue(), 'error': None}
        except Exception as e:
            __res = {'output': __string.getvalue(), 'error': type(e).__name__ + ': ' + str(e)}
        print(__json.dumps(__res))
