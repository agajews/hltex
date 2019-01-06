class Arg:
    def __init__(self, contents, optional=False):
        self.contents = contents
        self.optional = optional


def resolve_args(params, args):
    all_args = []
    arg_num = 0
    for param in self.params:
        if param == '!':
            if arg_num < len(args) and not args[arg_num].optional:
                all_args.append(args[arg_num])
                arg_num += 1
            elif arg_num >= len(args):
                raise TranslationError('Missing required argument for command `{}`'.format(self.name))
            else:
                raise TranslationError('Superfluous optional argument provided to command `{}`'.format(self.name))
        else:
            if arg_num < len(args) and args[arg_num].optional:
                all_args.append(args[arg_num])
                arg_num += 1
            else:
                all_args.append(None)
    return all_args

class Command:
    def __init__(self, name, translate_fn, params=''):
        self.name = name
        self.translate_fn = translate_fn
        self.params = params
        assert all([p in '!?' for p in params])

    def translate(self, args):
        return self.translate_fn(*resolve_args(self.params, args))


class Environment:
    def __init__(self, name, translate_fn, params=''):
        self.name = name
        self.translate_fn = translate_fn
        self.params = params
        assert all([p in '!?' for p in params])

    def translate(self, body, args):
        return self.translate_fn(body, *resolve_args(self.params, args))


def latex_cmd(name, args):
    return '\\%s%s' % (name, ''.join('{%s}' % arg for arg in args))


def latex_env(name, before='', body='', after='', args=''):
    return '\\begin{%s}%s%s%s%s\\end{%s}' % (name, args, before, body, after, name)


def translate_tbf(args):
    return latex_cmd('textbf', args)


commands = {
    'tbf': Command('tbf', translate_tbf, params='!')
}


def translate_eq(body, label):
    before = ''
    if label is not None:
        before = '\\label{%s}' % label
    return latex_env('equation', before=before, body=body)


environments = {
    'eq': Environment('eq', translate_eq, params='?')
}


class TranslationError(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__()


def isnewline(char):
    return char == '\n'


def iswhitespace(char):
    return str.isspace(char) and not isnewline(char)


def is_opt_end(char):
    return char in '#$%^&_{}[]~\\'


class Translator:
    def __init__(self, text):
        self.indent_str = None
        self.indent_level = 0

        self.pos = 0
        self.text = text

        self.in_document = False

    def parse_while(self, pred):
        '''
        pred: a boolean-valued function (i.e. a predicate) on a character
        postcondition: `self.pos` is at the first character *not* satisfying `pred`, after the original `self.pos` at call-time
        '''
        # TODO: deal with unexpected EOF
        while self.pos < len(self.text) and pred(self.text[self.pos]):
            self.pos += 1

    def parse_until(self, pred):
        '''
        pred: a boolean-valued function (i.e. a predicate) on a character
        postcondition: `self.pos` is at the first character satisfying `pred`, after the original `self.pos` at call-time
        '''
        self.parse_while(lambda c: not pred(c))

    def validate_indent(self, indent):
        '''
        indent: str
        errors: if `indent` is nonempty and isn't either all tabs or all spaces
        '''
        if not (all(s == ' ' for s in indent) or all(s == '\t' for s in indent)):
            self.error('Invalid indentation; must be all spaces or all tabs')  # TODO: more verbose errors

    def level_of_indent(self, indent):
        '''
        indent: str
        errors: if `len(indent)` isn't a multiple of `len(self.indent_str)`
        returns: the whole number of non-overlapping `self.indent_str` in `indent`
            (i.e. the indentation level where `self.indent_str` is the base unit of indentation)
        '''
        if not len(indent) % len(self.indent_str) == 0:
            self.error('Indentation must be in multiples of the base indentation `{}`'.format(
                self.indent_str))
        return len(indent) // len(self.indent_str)

    def calc_indent_level(self):
        # TODO: make sure self.pos actually is at the stat of a line
        '''
        precondition: `self.pos` is at the start of a line
        errors: if the current line isn't well-indented
        returns: the indentation level of the current line, in terms of `self.indent_str` units
        '''
        indent_start = self.pos
        self.parse_while(iswhitespace)
        indent = self.text[indent_start:self.pos]
        if len(indent) == 0:
            return 0
        self.validate_indent(indent)
        if self.indent_str == None:
            self.indent_str = indent
        indent_level = self.level_of_indent(indent)
        if indent_level > self.indent_level and not indent_level == self.indent_level + 1:
            self.error('You can only indent one level at a time')
        return self.level_of_indent(indent)

    def parse_empty(self):
        '''
        postcondition: `self.pos` is at the start of the next non-whitespace line, or at
            `len(self.text)` if there isn't a next non-whitespace line
        '''
        # print('parsing empty')
        while self.pos < len(self.text):
            # print(self.pos)
            line_end = self.text.find('\n', self.pos)
            if line_end == -1:
                line_end = len(self.text)
            if not str.isspace(self.text[self.pos:line_end + 1]):
                # print('`{}` is not a space'.format(self.text[self.pos:line_end]))
                break
            self.pos = line_end + 1

    def do_command(self, name):
        '''
        name: str representing the name of the current command
        precondition: `self.pos` is at the first character after the name of the command
            (e.g. a '{', but also possibly some whitespace)
        postcondition: `self.pos` is at the first character after the last argument of the command
            (or after the name for commands with no arguments)
        errors:
            if there are too few arguments
            if the arguments are ill-formed (e.g. contain environments)
        returns: a LaTeX string representing the result of the command
        '''
        command = commands[name]
        if command.nargs == 0:
            return command.translate([])
        args = []
        for arg in range(command.nargs):
            self.parse_while(iswhitespace)
            if self.text[self.pos] == '{':
                self.pos += 1
                args.append(self.extract_arg())
            else:
                self.error('Too few arguments provided to command `{}`'.format(name))
        return command.translate(args)

    def do_environment(self, name, args, argstr, for_document=False):
        '''
        name: str representing the name of the current environment
        args: a list of `Arg`s to pass to the environment if it's ours
        argstr: a LaTeX string containing the arguments to pass if it's a LaTeX environment
        for_document: bool, True if parsing the `document` environment (for the first time), False otherwise
        precondition: `self.pos` is at the first character after the colon
            (e.g. a `:`, but also possible some whitespace or a non-alph character for one-liners)
        postcondition:
            for one-liner environments, `self.pos` is at the newline at the end of the line
                or at `len(self.text)` if there isn't a trailing newline
            for block environments, `self.pos` is at the first non-whitespace character
                on the (dedented) line following the block, or at `len(self.text)` if
                the block is at the end of the file
        errors:
            if the line opening the environment is empty after the colon, but the following
                line isn't indented and the environment isn't the first `document` environment
            if there is indentation not following the opening of an environment
            if any indentation is ill-formed (e.g. not all tabs or spaces, or
                not a whole repetition of `self.indent_str`)
        '''
        self.parse_while(iswhitespace)
        if self.text[self.pos] == '\n':
            body = self.extract_block(for_environment=True, for_document=for_document)
        else:
            body_start = self.pos
            body_end = self.text.find('\n', self.pos)
            if body_end == -1:
                body_end = len(self.text)
            self.pos = body_end
            body = self.text[body_start:body_end]
        if name in environments:
            return environments[name].translate(body, args)
        else:
            return latex_env(name, body=body, args=argstr)

    def get_control_seq(self):
        '''
        precondition: `self.pos` is at the first character after the escape character ('\\')
        postcondition: `self.pos` is at the first character after the name of the command
            (including for control symbols, commands whose names are single special characters)
        returns: the name of the command
        '''
        control_start = self.pos
        self.parse_while(str.isalpha)
        if self.pos == control_start:
            self.pos += 1  # control symbols are only one character long
        # pos should be at the first non-alpha character
        control_seq = self.text[control_start:self.pos]
        return control_seq

    def extract_args(self, min_args = None, max_args=None):
        '''
        min_args: an int representing the minumum number of arguments to parse; None for no minimum
        max_args: an int representing the maximum number of arguments to parse; None for unlimited
        precondition: `self.pos` is at the first character after the name of the command
        postcondition: `self.pos` is at the first character after the last argument's closing brace or bracket
        errors: if there are fewer than `min_args` arguments following the command
        returns: a list of `Arg`s containing the parsed arguments, and a LaTeX string containing
            the arguments in case they are for a LaTeX command
        '''
        if max_args == 0:
            return command.translate([])
        args = []
        argstr = ''
        token_start = self.pos
        nargs = 0
        while True:
            self.parse_while(iswhitespace)
            if self.text[self.pos] == '{':  # TODO: make this less repetitive?
                self.pos += 1
                argstr += self.text[token_start:self.pos]
                token_start = self.pos
                arg = self.extract_arg(close='}')
                argstr += arg + '}'
                args.append(Arg(arg, optional=False))
                nargs += 1
            elif self.text[self.pos] == '[':
                self.pos += 1
                argstr += self.text[token_start:self.pos]
                token_start = self.pos
                arg = self.extract_arg(close=']')
                argstr += arg + ']'
                args.append(Arg(arg, optional=True))
                nargs += 1
            else:
                if min_args is not None and nargs < min_args:
                    self.error('Too few arguments provided')
                else:
                    break
            if max_args is not None and nargs >= max_args:
                break
        return args, argstr

    # def extract_opt(self):
    #     '''
    #     precondition: `self.pos` is at the first character following the opening '['
    #     postcondition: `self.pos` is at the first character following the closing `]`
    #     errors: if there is an invalid character before the closing `]`
    #     returns: the substring strictly between the opening and closing square brackets
    #     '''
    #     body_start = self.pos
    #     self.parse_until(is_opt_end)
    #     if self.text[self.pos] != ']':
    #         self.error('Invalid character `{}` in optional parameter'.format(self.text[self.pos]))
    #     body = self.text[body_start:self.pos]
    #     self.pos += 1
    #     return body

    def extract_arg(self, close='}'):
        '''
        close: the closing brace or bracket to the argument
        precondition: `self.pos` is at the first character following the opening '{' or '['
        postcondition: `self.pos` is at the first character following the closing '}' or ']';
            `extract_arg` ignores everything except for other commands inside the braces
        returns: the substring strictly between the opening and closing curly braces
        '''
        token_start = self.pos
        body = ''
        while self.pos < len(self.text):
            self.parse_until(lambda c: c == '\\' or c == close)
            if self.text[self.pos] == '\\':
                escape_start = self.pos
                self.pos += 1
                control_seq = self.get_control_seq()
                # if self.at_environment():
                #     self.error('You can\'t start an environment from a command body')
                body += self.text[token_start:escape_start]
                if control_seq in commands:
                    body += self.do_command(control_seq)
                else:
                    _, argstr = self.extract_args()
                    body += '\\' + control_seq + argstr
                    # TODO: issue a warning if the current character is a colon
                token_start = self.pos
            else:
                body += self.text[token_start:self.pos]
                self.pos += 1
            return body

    # def at_environment(self):
    #     # TODO: expand this to allow for other kinds of arguments
    #     # TODO: add support for '\\:' for literal colons
    #     '''
    #     precondition: `self.pos` is at the first character following the name of a control sequence
    #     postcondition: `self.pos` is in the same place where it started
    #     returns: True if the control sequence is followed by a colon (after optionally some arguments),
    #         indicating it is an environment, False otherwise
    #     '''
    #     old_pos = self.pos
    #     self.parse_while(iswhitespace)
    #     # print('checking at environment')
    #     # print(self.text[self.pos:self.pos+10])
    #     while self.pos < len(self.text):
    #     if self.text[self.pos] == '[':
    #         self.parse_until(is_opt_end)
    #         if self.text[self.pos] != ']':
    #             self.pos = old_pos
    #             return False
    #         self.pos += 1
    #     self.parse_while(iswhitespace)
    #     if self.text[self.pos] == ':':
    #         self.pos = old_pos
    #         return True
    #     self.pos = old_pos
    #     return False

    def extract_block(self, for_environment=False, for_document=False):
        # TODO: can this be broken up into smaller methods?
        '''
        precondition: `self.pos` is at the first newline after the colon for environments,
            or the beginning of the file for the outermost call
        postcondition: `self.pos` is at the first non-whitespace character of the line
            following the block, or at `len(self.text)` if the block is at the end of the file
        errors:
            if there is an ill-formed environment (e.g. not indended after and not a one-liner)
            if there is indentation not following the opening of an environment
            if any indentation is ill-formed (e.g. not all tabs or spaces, or
                not a whole repetition of `self.indent_str`)
        returns: the substring containing everything from the original value of `self.pos`
            at calltime through and including the newline before the next non-whitespace
            line, or through the end of the file if the block is at the end of the file
        '''
        body = ''
        # print('starting block at {}, `{}`'.format(self.pos, self.text[self.pos:self.pos+10]))
        token_start = self.pos
        self.parse_empty()
        # print('finished parsing empty')
        indent_level = self.calc_indent_level()
        # print(indent_level)
        if for_environment and not for_document and not indent_level == self.indent_level + 1:
            self.error('You must either put the body of an environment all on one line, or on an indented block on the following line')
        elif not for_environment and not indent_level == 0:
            self.error('The document as a whole must not be indented')
        indented = indent_level == self.indent_level + 1
        block_indent = self.indent_level
        self.indent_level = indent_level

        while self.pos < len(self.text):
            self.parse_until(lambda c: c == '\\' or c == '\n')
            if self.text[self.pos] == '\n':
                self.parse_empty()
                line_start = self.pos
                indent_level = self.calc_indent_level()
                # print(indent_level)
                if indent_level > self.indent_level:
                    self.error('Invalid indentation not following the opening of an environment')
                elif indented:
                    if indent_level <= block_indent:
                        body += self.text[token_start:line_start + 1]
                        # pos is at the first non-whitespace of the line
                        return body
                    else:
                        # print(self.pos)
                        # print(self.text[self.pos:self.pos + 10])
                        raise Exception('When would this happen?')  # TODO: be better about this error

            elif self.text[self.pos] == '\\':
                # print('Found escape at pos {}'.format(self.pos))
                escape_start = self.pos
                self.pos += 1
                control_seq = self.get_control_seq()
                # print(control_seq)
                body += self.text[token_start:escape_start]
                if control_seq in commands:
                    body += self.do_command(control_seq)
                else:
                    args, argstr = self.extract_args()
                    whitespace_start = self.pos
                    self.parse_while(iswhitespace)
                    if self.text[self.pos] == ':':
                        self.pos += 1
                        # print('at environment')
                        for_document = False
                        if not self.in_document and control_seq == 'document':
                            self.in_document = True
                            for_document = True
                        # print('Doing environment `{}`'.format(control_seq))
                        body += self.do_environment(control_seq, args, argstr, for_document=for_document)
                        token_start = self.pos
                    else:
                        body += '\\' + control_seq + argstr + self.text[whitespace_start:self.pos]
                token_start = self.pos
        body += self.text[token_start:]
        return body


    def translate(self):
        # import pdb;pdb.set_trace()
        try:
            return self.extract_block()
        except TranslationError as e:
            self.print_error(e.msg)  # XXX: check whether this works (is it .msg?)

    def error(self, msg):
        raise TranslationError(msg)

    def print_error(self, msg):
        print('{} at char {}'.format(msg, self.pos))  # TODO: better errors