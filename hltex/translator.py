class Command:
    def __init__(self, name, translate_fn, nargs=0):
        self.name = name
        self.nargs = nargs
        self.translate_fn = translate_fn

    def translate(self, args=None):
        return self.translate_fn(args)


class Environment:
    def __init__(self, name, translate_fn):
        self.name = name
        self.translate_fn = translate_fn

    def translate(self, body, opt=None):
        return self.translate_fn(body, opt)


def latex_cmd(name, args):
    return '\\%s%s' % (name, ''.join('{%s}' % arg for arg in args))


def latex_env(name, before='', body='', after=''):
    return '\\begin{%s}%s%s%s\\end{%s}' % (name, before, body, after, name)


def translate_tbf(args):
    return latex_cmd('textbf', args)


commands = {
    'tbf': Command('tbf', translate_tbf, nargs=1)
}


def translate_eq(body, label):
    before = ''
    if label is not None:
        before = '\\label{%s}' % label
    return latex_env('equation', before=before, body=body)


environments = {
    'eq': Environment('eq', translate_eq)
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
        # TODO: deal with unexpected EOF
        while self.pos < len(self.text) and pred(self.text[self.pos]):
            self.pos += 1

    def parse_until(self, pred):
        self.parse_while(lambda c: not pred(c))

    def validate_indent_str(self):
        if not (all(s == ' ' for s in self.indent_str) or all(s == '\t' for s in self.indent_str)):
            self.error('Invalid indentation; must be all spaces or all tabs')  # TODO: more verbose errors

    def level_of_indent(self, indent):
        if not len(indent) % len(self.indent_str) == 0:
            self.error('Indentation must be in multiples of the base indentation `{}`'.format(
                self.indent_str))
        return len(indent) // len(self.indent_str)

    def calc_indent_level(self):
        indent_start = self.pos
        self.parse_while(iswhitespace)  # precondition: we assume the current line isn't empty
        indent = self.text[indent_start:self.pos]
        if len(indent) == 0:
            return 0
        if self.indent_str == None:
            self.indent_str = indent
            self.validate_indent_str()
        indent_level = self.level_of_indent(indent)
        if indent_level > self.indent_level and not indent_level == self.indent_level + 1:
            self.error('You can only indent one level at a time')
        return self.level_of_indent(indent)

    def parse_empty(self):
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
        command = commands[name]
        if command.nargs == 0:
            return command.translate([])
        args = []
        for arg in range(command.nargs):
            self.parse_while(iswhitespace)
            if self.text[self.pos] == '{':
                args.append(self.extract_arg())
            else:
                self.error('Too few arguments provided to command `{}`'.format(name))
        return command.translate(args)

    def do_environment(self, name, for_document=False):
        self.parse_while(iswhitespace)
        opt = None
        if self.text[self.pos] == '[':
            body = self.extract_opt()
            opt = body
        self.parse_while(iswhitespace)
        if self.text[self.pos] == ':':
            self.pos += 1
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
                return environments[name].translate(body, opt)
            else:
                return latex_env(name, body=body)
        else:
            self.error('Environments must be followed by colons')

    def get_control_seq(self):
        control_start = self.pos
        self.parse_while(str.isalpha)
        if self.pos == control_start:
            self.pos += 1  # control symbols are only one character long
        # pos should be at the first non-alpha character
        control_seq = self.text[control_start:self.pos]
        return control_seq

    def extract_opt(self):
        body_start = self.pos
        self.parse_until(is_opt_end)
        if self.text[self.pos] != ']':
            self.error('Invalid character `{}` in optional parameter'.format(self.text[self.pos]))
        body = self.text[body_start:self.pos]
        self.pos += 1
        return body

    def extract_arg(self):
        token_start = self.pos
        body = ''
        while self.pos < len(text):
            self.parse_until(lambda c: c == '\\' or c == '}')
            if self.text[self.pos] == '\\':
                escape_start = self.pos
                self.pos += 1
                control_seq = self.get_control_seq()
                if control_seq in environments:
                    self.error('You can\'t start an environment from a command body')
                elif control_seq in commands:
                    body += self.text[token_start:escape_start]
                    body += self.do_command(control_seq)
                    token_start = self.pos
            else:
                body += self.text[token_start:self.pos]
                self.pos += 1
            return body

    def at_environment(self):
        old_pos = self.pos
        self.parse_while(iswhitespace)
        # print('checking at environment')
        # print(self.text[self.pos:self.pos+10])
        if self.text[self.pos] == '[':
            self.parse_until(is_opt_end)
            if self.text[self.pos] != ']':
                self.pos = old_pos
                return False
            self.pos += 1
        self.parse_while(iswhitespace)
        if self.text[self.pos] == ':':
            self.pos = old_pos
            return True
        self.pos = old_pos
        return False

    def extract_block(self, for_environment=False, for_document=False):
        # TODO: can this be broken up into smaller methods?
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
                    self.error('Invalid indentation')  # TODO: be more verbose
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
                if self.at_environment():  # TODO: make this more concise?
                    # print('at environment')
                    body += self.text[token_start:escape_start]
                    for_document = False
                    if not self.in_document and control_seq == 'document':
                        self.in_document = True
                        for_document = True
                    # print('Doing environment `{}`'.format(control_seq))
                    body += self.do_environment(control_seq, for_document=for_document)
                    token_start = self.pos
                elif control_seq in commands:
                    body += self.text[token_start:escape_start]
                    body += self.do_command(control_seq)
                    token_start = self.pos
        body += self.text[token_start:]
        return body


    def translate(self):
        try:
            return self.extract_block()
        except TranslationError as e:
            self.print_error(e.msg)  # XXX: check whether this works (is it .msg?)

    def error(self, msg):
        raise TranslationError(msg)

    def print_error(self, msg):
        print('{} at char {}'.format(msg, self.pos))  # TODO: better errors
