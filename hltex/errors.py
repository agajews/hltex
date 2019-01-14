class TranslationError(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__()


class InternalError(TranslationError):
    def __init__(self):
        super().__init__("Something went wrong")


class UnexpectedEOF(TranslationError):
    def __init__(self, msg):
        super().__init__(msg)


class MissingArgument(TranslationError):
    def __init__(self, msg):
        super().__init__(msg)


class InvalidIndentation(TranslationError):
    def __init__(self, msg):
        super().__init__(msg)


class UnexpectedIndentation(TranslationError):
    def __init__(self, msg):
        super().__init__(msg)


class InvalidSyntax(TranslationError):
    def __init__(self, msg):
        super().__init__(msg)
