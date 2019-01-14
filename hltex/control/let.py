"""
four kinds of control sequence definitions: let, def, letenv, defenv
let is exactly like newcommand
def defines hltex commands that are re-expanded by hltex (as opposed to tex) after being parsed
this allows things like defining a custom pyfig-like command *in hltex*
letenv is like let but for environments
defenv is like def but for environments

what I want is to be able to have control sequences trigger new parse contexts like they do in plain Tex
what would this entail? refactoring the parser to have parse contexts that trigger other parse contexts.
what would this look like? a parse context is a function that takes a string (the text) and a parse position
(previously self.pos), and returns a string (the resulting latex code), a parse position, and
the name of the next context to go to.
"""
