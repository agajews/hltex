def parse_while(state, pred):
    """
    pred: a boolean-valued function (i.e. a predicate) on a character
    postcondition: `state.pos` is at the first character *not* satisfying `pred`,
        after the original `state.pos` at call-time, or `len(self.text)` if there is
        no such character
    returns: the text satisfying `pred` starting from the original `state.pos`
    """
    start = state.pos
    while not state.finished() and pred(state.text[state.pos]):
        state.pos += 1
    return state.text[start : state.pos]


def parse_until(state, pred):
    """
    pred: a boolean-valued function (i.e. a predicate) on a character
    postcondition: `state.pos` is at the first character satisfying `pred`,
        after the original `state.pos` at call-time, or `len(self.text)` if there is
        no such character
    returns: the text *not* satisfying `pred` starting from the original `state.pos`
    """
    return parse_while(state, pred=lambda c: not pred(c))


def increment(state):
    """
    postcondition: `state.pos` is incremented, unless `state.pos` was already at least
        `len(state.text)`
    returns: the character at `state.text[state.pos]`, or the empty string if `state.pos`
        was not incremented
    """
    if not state.finished():
        state.pos += 1
        return state.text[state.pos - 1 : state.pos]
    return ""
