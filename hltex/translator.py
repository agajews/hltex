import sys
import os
import json
import traceback
import tempfile
import warnings
from textwrap import dedent

hlbox = None


class Arg:
    def __init__(self, contents, optional=False):
        self.contents = contents
        self.optional = optional

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def resolve_args(name, params, args):
    '''
    params: a string consisting of `!`s and `?`s, where `!`s represent required arguments
        and `!`s represent optional arguments
    args: a list of `Arg`s to be resolved with the `params` string
    errors: if there is a missing required argument or a superfluous optional argument
    returns: a list of `Arg`s with additional `None`s for missing optional arguments
    raises: Exception if passed more args than params
    '''
    all_args = []
    arg_num = 0
    if len(args) > len(params):
        raise TranslationError('Too many arguments while resolving arguments for {}'.format(name))
    for param in params:
        if param == '!':
            if arg_num < len(args) and not args[arg_num].optional:
                all_args.append(args[arg_num].contents)
                arg_num += 1
            elif arg_num >= len(args):
                raise TranslationError('Missing required argument for command `{}`'.format(name))
            else:
                raise TranslationError('Superfluous optional argument provided to command `{}`'.format(name))
        else:
            if arg_num < len(args) and args[arg_num].optional:
                all_args.append(args[arg_num].contents)
                arg_num += 1
            else:
                all_args.append(None)
    return all_args


def unresolve_args(args):
    argstr = ''
    for arg in args:
        if arg is not None and arg.contents is not None:
            argstr += '[%s]' % arg.contents if arg.optional else '{%s}' % arg.contents
    return argstr

class Command:
    def __init__(self, name, translate_fn, params='', is_raw=False):
        self.name = name
        self.translate_fn = translate_fn
        self.params = params
        self.is_raw = is_raw
        assert all([p in '!?' for p in params])

    def translate(self, translator, args):
        return self.translate_fn(translator, *resolve_args(self.name, self.params, args))


class Environment:
    def __init__(self, name, translate_fn, params='', is_raw=False):
        self.name = name
        self.translate_fn = translate_fn
        self.params = params
        self.is_raw = is_raw
        assert all([p in '!?' for p in params])

    def translate(self, translator, body, args):
        try:  # XXX: why?
            return self.translate_fn(translator, body, *resolve_args(self.name, self.params, args))
        except TranslationError as e:
            raise e

def latex_cmd(name, *args):
    return '\\%s%s' % (name, unresolve_args(args))


def latex_env(name, before='', body='', after='', args='', post_env=''):
    return '\\begin{%s}%s%s%s%s\\end{%s}%s' % (name, args, before, body, after, name, post_env)


def translate_docclass(translator, opts, arg):
    return latex_cmd('documentclass', Arg(opts, optional=True), Arg(arg))

def translate_verb(translator, body):
    return latex_cmd('verb', Arg(body))

commands = {
    'docclass': Command('docclass', translate_docclass, params='?!'),
    'verb': Command('verb', translate_verb, params='!', is_raw=True),
    'colon': Command('colon', lambda _: ':', params='')
}


def translate_eq(translator, body, label):
    before = ''
    if label is not None:
        before = '\\label{eq:%s}' % label
    return latex_env('equation', before=before, body=body)


def translate_pysplice(translator, body):
    '''
    Executes the body as a python snippet using epicbox
    '''
    global hlbox
    if hlbox is None or translator.sandbox is None:
        try:
            import hlbox

            hlbox.configure(
                profiles=[
                    hlbox.Profile('python', 'czentye/matplotlib-minimal')
                ]
            )

            files = [{'name': 'main.py', 'content': dedent(
                '''
                import json as __json
                import io as __io
                from textwrap import indent as __indent
                from contextlib import redirect_stdout as __redirect_stdout


                if __name__ == '__main__':
                    while True:
                        __code = input()
                        __request = eval(__code)
                        if isinstance(__request, bool):
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
                ''').encode('utf-8')}]

            for name, content in translator.file_env.items():
                files.append({'name': name, 'content': content.encode('utf-8')})

            limits = {'cputime': 10, 'memory': 64}
            translator.sandbox = hlbox.create('python', 'python3 -u main.py', files=files, limits=limits, prep_download=True)

        except Exception as e:
            raise TranslationError("Failed to configure HLBox for pysplice. Make sure you have HLBox and Docker installed and configured.\n"
                                    + str(e))

    body = dedent(body).encode('utf-8')
    # print('Running line...')
    result = hlbox.runline(translator.sandbox, repr(body) + '\n')
    # print('Got ', result)
    # result = hlbox.run('python', 'python3 main.py', files=files, limits=limits, download_target=tmp_dir)

    if result['exit_code'] != 0:
        # err_msg = "Pysplice execution failed.\nCode block:\n{}\n\nOutput:\n{}".format(body, str(result))
        # err_lines = result['stderr'].decode('utf-8').split('\n')
        # err = err_lines[-2] if len(err_lines) else ''
        err_msg = "Pysplice execution failed"
        raise TranslationError(err_msg)

    output = json.loads(result['stdout'].decode('utf-8'))
    if output['error'] is not None:
        raise TranslationError('Pysplice execution failed: {}'.format(output['error']))
    return output['output']

def translate_verbatim(translator, body):
    return latex_env('verbatim', body=body)

environments = {
    'eq': Environment('eq', translate_eq, params='?'),
    'pysplice': Environment('pysplice', translate_pysplice, is_raw=True),
    'verbatim': Environment('verbatim', translate_verbatim, is_raw=True)
}


class TranslationError(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__()


def isnewline(char):
    return char == '\n'


def iswhitespace(char):
    return str.isspace(char) and not isnewline(char)


# def is_opt_end(char):
#     return char in '#$%^&_{}[]~\\'


class Translator:
    def __init__(self, text, file_env={}):
        self.indent_str = None
        self.indent_level = 0

        self.pos = 0
        # we will often increment pos by 1 when we expect a control seq/block to end
        # this prevents us from going out of bounds (in general it's a good idea to end file with \n)
        if not text or text[-1] != '\n':
            text += '\n'
        self.text = text
        self.preamble = False

        self.generated_files = []
        self.file_env = file_env

        self.sandbox = None

    def finished(self):
        assert self.pos <= len(self.text)
        return self.pos == len(self.text)

    def not_finished(self):
        return not self.finished()

    def check_for_document_begin(self):
        '''
        precondition: at previous end-of-line
        postcondition: self.pos remain the same UNLESS we enter the document from preamble,
            in which case it's at the next new line
        Checks for ===, the separator between preamble and document

        return: spacing needed before \begin{document}
        '''
        if self.indent_level != 0 or not self.preamble:
            return False

        # at root level in preamble; lines must start with \ or ===
        token_start = self.pos
        self.parse_empty()
        line_start = self.pos
        self.parse_while(iswhitespace)
        if self.text[self.pos] == '=':
            separator_start = self.pos
            self.parse_while(lambda c: c == '=')
            if self.pos - separator_start < 3:
                self.error("Separator indicating start of document must be at least '===' (3 equal signs).")

            self.parse_while(iswhitespace)
            if self.finished() or self.text[self.pos] == '\n':
                self.preamble = False

                return self.text[token_start:line_start]

        elif self.text[self.pos] not in ['\\', '%', '\n', '=']:
            self.error("Preamble lines must start with \\.")

        self.pos = token_start
        return False

    def parse_while(self, pred):
        '''
        pred: a boolean-valued function (i.e. a predicate) on a character
        postcondition: `self.pos` is at the first character *not* satisfying `pred`, after the original `self.pos` at call-time,
            or `len(self.text)` if there is no such character
        '''
        # TODO: deal with unexpected EOF
        while self.not_finished() and pred(self.text[self.pos]):
            self.pos += 1

    def parse_until(self, pred):
        '''
        pred: a boolean-valued function (i.e. a predicate) on a character
        postcondition: `self.pos` is at the first character satisfying `pred`, after the original `self.pos` at call-time,
            or `len(self.text)` if there is no such character
        '''
        self.parse_while(lambda c: not pred(c))

    def validate_indent(self, indent):
        '''
        indent: str
        errors: if `indent` is nonempty and isn't either all tabs or all spaces
        '''
        if not (all(s == ' ' for s in indent) or all(s == '\t' for s in indent)):
            self.error('Invalid indentation; must be all spaces or all tabs')  # TODO: more verbose errors

    def level_of_indent(self, indent, validate=True):
        '''
        indent: str
        precondition: `self.indent_str` is not None
        validate: False if we don't care about indentation correctness, e.g. if we're in a raw block

        errors: if `len(indent)` isn't a multiple of `len(self.indent_str)`
        returns: the whole number of non-overlapping `self.indent_str` in `indent`
            (i.e. the indentation level where `self.indent_str` is the base unit of indentation)
        '''
        if validate and not len(indent) % len(self.indent_str) == 0:
            self.error('Indentation must be in multiples of the base indentation `{}`'.format(
                self.indent_str))
        return len(indent) // len(self.indent_str)

    def calc_indent_level(self, validate=True):
        '''
        precondition: `self.pos` is at the start of a line
        postcondition: `self.pos` is where it started
        validate: False if we don't care about indentation correctness, e.g. if we're in a raw block
        errors: if the current line isn't well-indented (e.g. if it is more than one
            deeper than the current level)
        returns: the indentation level of the current line, in terms of `self.indent_str` units
        '''
        if validate: assert self.pos == 0 or self.finished() or isnewline(self.text[self.pos - 1]), "pos: {}, text: {}".format(self.pos, self.text[self.pos-1:self.pos+10])

        indent_start = self.pos
        self.parse_while(iswhitespace)
        indent = self.text[indent_start:self.pos]
        if len(indent) == 0:
            self.pos = indent_start
            return 0
        if validate: self.validate_indent(indent)
        if self.indent_str == None:
            self.indent_str = indent
        indent_level = self.level_of_indent(indent, validate)
        if validate and self.indent_level == -1 and indent_level != 0:
            self.error('The document as a whole must not be indented')
        self.pos = indent_start
        return indent_level

    def parse_empty(self):
        '''
        postcondition: `self.pos` is at the start of the next non-whitespace line (i.e.
            after the preceeding newline), or at `len(self.text)` if there isn't a
            next non-whitespace line
        '''
        while self.not_finished():
            line_end = self.text.find('\n', self.pos)
            if line_end == -1:
                line_end = len(self.text) - 1
            if not str.isspace(self.text[self.pos:line_end + 1]):
                # print('`{}` is not a space'.format(self.text[self.pos:line_end]))
                break
            self.pos = line_end + 1

    def parse_comments(self):
        '''
        precondition: `self.pos` is at '%', start of a comment
        postcondition: `self.pos` is at the start of the next non-whitespace line (i.e.
            after the preceeding newline), or at `len(self.text)` if there isn't a
            next non-whitespace line

        What this is really doing is just to parse this line and then any all-white lines after
        '''
        self.parse_until(isnewline)
        self.parse_empty()

    def parse_control_seq(self):
        '''
        precondition: `self.pos` is at the first character after the escape character ('\\')
        postcondition: `self.pos` is at the first character after the name of the command
            (including for control symbols, commands whose names are single special characters),
            or at `len(self.text)` if there isn't a character after the command name
        returns: the name of the command
        '''
        control_start = self.pos
        self.parse_while(str.isalpha)
        if self.pos == control_start:
            self.pos += 1  # control symbols are only one character long
        # pos should be at the first non-alpha character
        control_seq = self.text[control_start:self.pos]
        return control_seq


    def parse_backslash(self, allow_env=True):
        '''
        precondition: `self.pos` is at \\
        '''
        assert self.text[self.pos] == '\\', self.pos
        self.pos += 1
        control_seq = self.parse_control_seq()
        body = ''

        if control_seq in commands:
            body += self.do_command(commands[control_seq])
        else:
            args, argstr = self.parse_args()  # TODO: allow raw args in environments?
            whitespace_start = self.pos
            self.parse_while(iswhitespace)
            if self.not_finished() and self.text[self.pos] == ':':
                if not allow_env:
                    self.warn('Nested environments not supported inside oneline environments.')
                    return body

                self.pos += 1
                # print('at environment')
                # print('Doing environment `{}`'.format(control_seq))
                if control_seq in environments:
                    environment = environments[control_seq]
                else:
                    environment = control_seq

                outer_indent = self.indent_level

                body += self.do_environment(environment, args, argstr, outer_indent)
            else:
                body += '\\' + control_seq + argstr + self.text[whitespace_start:self.pos]

        #print('parsing backslash: {} line {} pos {}'.format(self.text[self.pos], self.get_line(), self.pos))
        #self.pos -= 1
        return body

    def parse_arg(self, close='}', required=False, is_raw=False):
        '''
        close: the closing brace or bracket to the argument
        required: whether to error if no closing brace or bracket is found
        is_raw: whether the argument is raw (only waiting for unescaped close character)
        precondition: `self.pos` is at the first character following the opening '{' or '['
        postcondition: `self.pos` is at the first character following the closing '}' or ']',
            or at `len(self.text)` if there is no such character; `parse_arg` ignores
            everything except for other commands inside the braces;
            we also skip over comments, ignoring everything from '%' up to the end of line
        errors: if `required` and the file ends before there is a `close` character
        returns: the substring strictly between the opening and closing curly braces
        '''
        token_start = self.pos
        body = ''
        while self.not_finished():
            self.parse_until(lambda c: c == close or (not is_raw and (c == '\\' or c == '{' or c == '%')))
            if self.not_finished():
                if self.text[self.pos] == '{':
                    body += self.text[token_start:self.pos]
                    self.pos += 1
                    body += '{' + self.parse_arg(required=True) + '}'
                elif self.text[self.pos] == '\\':
                    body += self.text[token_start:self.pos]

                    body += self.parse_backslash()

                elif self.text[self.pos] == close:
                    if is_raw and self.text[self.pos-1] == '\\':
                        self.pos += 1
                        continue  # escaped close }, skip

                    body += self.text[token_start:self.pos]
                    self.pos += 1
                    return body

                elif self.text[self.pos] == '%':
                    body += self.text[token_start:self.pos]
                    self.parse_comments()

                token_start = self.pos

        if required:
            self.error('Missing closing `{}`'.format(close))
        else:
            return None

    def parse_args(self, min_args=None, max_args=None, is_raw=False):
        '''
        min_args: an int representing the minumum number of arguments to parse; None for no minimum
        max_args: an int representing the maximum number of arguments to parse; None for unlimited
        precondition: `self.pos` is at the first character after the name of the command
        postcondition: `self.pos` is at the first character after the last argument's closing brace or bracket
        errors: if there are fewer than `min_args` arguments following the command
        returns: (args, argstring) -- a list of `Arg`s containing the parsed arguments, and the original LaTeX string.
            Comments will be included in argstring but not in args
        '''
        if max_args == 0:
            return command.translate(self, [])
        args = []
        parse_start = self.pos
        nargs = 0
        while True:
            self.parse_while(iswhitespace)
            if self.finished():
                break

            if self.text[self.pos] == '{':  # TODO: make this less repetitive?
                self.pos += 1
                arg = self.parse_arg(close='}', required=True, is_raw=is_raw)
                args.append(Arg(arg, optional=False))
                nargs += 1
            elif self.text[self.pos] == '[':
                arg_start = self.pos
                self.pos += 1
                arg = self.parse_arg(close=']', is_raw=is_raw)
                if arg is not None:
                    args.append(Arg(arg, optional=True))
                    nargs += 1
                else:
                    self.pos = arg_start
                    break
            else:
                if min_args is not None and nargs < min_args:
                    self.error('Too few arguments provided')
                else:
                    break
            if max_args is not None and nargs >= max_args:
                break

        argstr = self.text[parse_start:self.pos]
        return args, argstr

    def do_command(self, command):
        '''
        command: `Command` object representing the command to execute
        precondition: `self.pos` is at the first character after the name of the command
            (e.g. a '{', but also possibly some whitespace)
        postcondition: `self.pos` is at the first character after the last argument of the command
            (or after the name for commands with no arguments)
        errors:
            if there are too few arguments
            if the arguments are ill-formed (e.g. contain environments)
        returns: a LaTeX string representing the result of the command
        '''
        if len(command.params) == 0:  # this is just for efficiency
            return command.translate(self, [])
        args, argstr = self.parse_args(max_args=len(command.params), is_raw=command.is_raw)
        return command.translate(self, args)

    def do_environment(self, environment, args, argstr, outer_indent):
        # TODO: ensure the translate_fn use the same indent string and starts the block with 0 indent,
        #       then we'll wrap this block with the correct indentation level
        '''
        environment: either an `Environment` object to do the translation, or a string,
            the name of a LaTeX environment for which to insert a corresponding begin/end
        args: a list of `Arg`s to pass to the environment if it's ours
        argstr: a LaTeX string containing the arguments to pass if it's a LaTeX environment
        outer_indent: indentation level of the enclosing environment, or 0 if unenclosed

        precondition: `self.pos` is at the first character after the colon
            (e.g. a newline, but also possibly some other whitespace or a non-alph character for one-liners)
        postcondition:
            `self.pos` is at the end `\n` of the block, both for one-liner and for indented blocks
        errors:
            if the line opening the environment is empty after the colon, but the following
                line isn't indented and the environment isn't the first `document` environment
            if there is indentation not following the opening of an environment
            if any indentation is ill-formed (e.g. not all tabs or spaces, or
                not a whole repetition of `self.indent_str`)
        returns: a translated LaTeX string for the environment
        '''
        #print('do environment: ', environment.name if isinstance(environment, Environment) else str(environment))
        is_raw = isinstance(environment, Environment) and environment.is_raw

        token_start = self.pos
        body = ''
        post_env = ''

        self.parse_while(iswhitespace)
        if self.finished():
            #print("at end of do_environment ...remaining text: {}".format(body, self.text[token_start:]))
            body += self.text[token_start:]
        else:
            if self.text[self.pos] == '\n':
                #print('start env: ', self.pos, self.get_line(), environment.name if isinstance(environment, Environment) else str(environment), self.indent_level, outer_indent)
                body += self.parse_block(is_raw=is_raw)
                if body[-1] != '\n':
                    body += '\n'
                #print('end env: ', self.pos, self.get_line(), environment.name if isinstance(environment, Environment) else str(environment), self.indent_level, outer_indent)
                if outer_indent > 0:
                    body += self.indent_str * outer_indent
            else:
                # For one-liners, we keep the whitespace we've parsed over
                while self.not_finished():
                    self.parse_until(lambda c: c in ['\n', '\\', '%'])
                    if self.finished() or self.text[self.pos] == '\n':
                        body += self.text[token_start:self.pos]
                        #self.pos += 1  # skip over the end line
                        break

                    elif self.text[self.pos] == '\\':
                        body += self.text[token_start:self.pos]
                        body += self.parse_backslash(allow_env=False)
                        token_start = self.pos

                    elif self.text[self.pos] == '%':  # include the comments but ignore any \\
                        body += self.text[token_start:self.pos]
                        comment_start = self.pos
                        self.parse_comments()
                        post_env = self.text[comment_start:self.pos]  # put these after \end{...} on the same line
                        break

        if isinstance(environment, Environment):
            return environment.translate(self, body, args) + post_env
        else:
            return latex_env(environment, body=body, args=argstr, post_env=post_env)


    def parse_block(self, is_raw=False):
        # TODO: can this be broken up into smaller methods?
        '''
        precondition: `self.pos` is at the first newline after the colon for environments,
            or the beginning of the file for the outermost call
        postcondition: `self.pos` is at the endline `\n` following the block, or at
            `len(self.text)` if the block is at the end of the file
        errors:
            if there is an ill-formed environment (e.g. not indended after and not a one-liner)
            if there is indentation not following the opening of an environment
            if any indentation is ill-formed (e.g. not all tabs or spaces, or
                not a whole repetition of `self.indent_str`)
        returns: the substring containing everything from the original value of `self.pos`
            at calltime through and including the newline before the next non-whitespace
            line, or through the end of the file if the block is at the end of the file

            If is_raw is True, then return the block of text unmodified
        '''

        body = ''
        #print('starting block at {}, line {}, indent: {}'.format(self.pos, self.get_line(), self.indent_level))
        token_start = self.pos

        self.parse_empty()
        indent_level = self.calc_indent_level(not is_raw)
        # print(indent_level)

        if not is_raw and indent_level != self.indent_level + 1:
            self.error('Indent Error. You must either put the body of an environment all on one line, or on an indented block on the following line')

        prev_block_indent = self.indent_level
        self.indent_level += 1

        while self.not_finished():
            # precondition: endline \n
            space_before_document = self.check_for_document_begin()
            if space_before_document != False:
                self.indent_level = -1
                body += space_before_document

                # Maybe: two lines separating preamble and main?
                return body + latex_env("document", '', self.parse_block(), '', '', '\n')

            self.parse_until(lambda c: c == '\n' or (not is_raw and (c == '\\' or c == '%')))
            if self.finished():
                break

            if self.text[self.pos] == '\n':
                prev_line_end = self.pos

                self.parse_empty()
                indent_level = self.calc_indent_level(not is_raw)
                #print(indent_level, prev_line_end, prev_block_indent, self.indent_level)

                if not is_raw and indent_level > self.indent_level:
                    self.error('Invalid indentation not following the opening of an environment')

                if indent_level <= prev_block_indent:  # unindent, end block
                    # save the white space for outside the environment
                    self.pos = prev_line_end# + 1
                    body += self.text[token_start:self.pos]
                    self.indent_level = indent_level
                    return body

            elif self.text[self.pos] == '\\':
                body += self.text[token_start:self.pos]
                body += self.parse_backslash()
                token_start = self.pos

            elif self.text[self.pos] == '%':  # include the comments but ignore any \\
                self.parse_comments()
                body += self.text[token_start:self.pos]
                token_start = self.pos

        #print("at end of parse_block... body {} remaining text: {}".format(body, self.text[token_start:]))

        body += self.text[token_start:]
        if body[-1] != '\n':
            body += '\n'
        return body

    def get_line(self):
        return self.text.count('\n', 0, self.pos)

    def fetch_generated_files(self):
        tmp_dir = os.path.join(tempfile._get_default_tempdir(),
                            'hltex_python_' + next(tempfile._get_candidate_names()))
        os.mkdir(tmp_dir)
        hlbox.runline(self.sandbox, 'False\n')  # trigger tar
        hlbox.download(self.sandbox, tmp_dir)

        for f in os.listdir(tmp_dir):
            if os.path.isfile(os.path.join(tmp_dir, f)) and f != 'main.py':
                self.generated_files.append(os.path.join(tmp_dir, f))


    def parse_file(self):
        self.preamble = True
        self.indent_level = -1  # to simulate document block being indented as if it's a command
        res = self.parse_block()

        self.fetch_generated_files()
        if self.sandbox is not None:
            hlbox.destroy(self.sandbox)

        return res

    def translate(self):
        #import pdb;pdb.set_trace()
        try:
            res = self.parse_file()
            # print(self.generated_files)
            return res
        except TranslationError as e:
            self.print_error(e.msg, self.get_line())

    def translate_internal(self):
        try:
            return {'text': self.parse_file(), 'error': None, 'line': None, 'files': self.generated_files}
        except TranslationError as e:
            traceback.print_exc()
            return {'text': None, 'error': e.msg, 'line': self.get_line(), 'files': []}

    def error(self, msg):
        raise TranslationError(msg)

    def warn(self, msg):
        warnings.warn(msg)

    def print_error(self, msg, line):
        ## TODO: prettier errors (line number, another line with ^ pointing to error character, etc.)
        sys.stderr.write('{} at line {}, char {} (next 10 chars: {})\n'.format(
            msg, line, self.pos, repr(self.text[self.pos:self.pos+10])))  # TODO: better errors


def prepTranslator(source, indent_level=0):
    translator = Translator(source)
    translator.indent_str = '    '
    translator.indent_level = indent_level
    return translator
