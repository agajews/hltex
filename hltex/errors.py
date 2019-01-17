class TranslationError(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__()


class InternalError(TranslationError):
    def __init__(self):
        super().__init__("Something went wrong")


class UnexpectedEOF(TranslationError):
    pass


class MissingArgument(TranslationError):
    pass


class InvalidIndentation(TranslationError):
    pass


class UnexpectedIndentation(TranslationError):
    pass


class InvalidSyntax(TranslationError):
    pass
