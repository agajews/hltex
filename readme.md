# HLTeX (Provisional Name)
HLTeX is a new typesetting language built on top of LaTeX designed for conciseness and ease of use,
while also adding support for additional features like inline Matplotlib figure generation
and SymPy integration

### Example
```
\documentclass{article}
\title{My First Document}
\author{Your Truly}
===
\section{HLTeX is Awesome}
Here are some words that are in this section.
Math is fun, so here's an equation:
\eq:
    f(x) = x^2 + 3
We might want to give our equation a label, like this:
\eq[cubic]:
    f(x) = x^3 - 4x^2 + 2
We can reference our equation with Equation \ref{eq:cubic}.
This is automatically joined with the non-breaking space \verb{~}.
```

### Syntax
HLTeX supports two kinds of macros: *commands* and *environments*.

Commands are just as they are in plain LaTeX, and they look like this:
```
This text \\emph{is emphasized} using the \\\\emph command.
```
They are preceeded by a backslash, the *escape character*, followed by either any number of letters in the alphabet
(capital or lowercase), or by a single non-alphabetical character, as in the backslash literal in the example above.

Environments are slightly different in HLTeX than in LaTeX.
Whereas in LaTeX they are enclosed by begin/end commands, in HLTeX environments use indentation-based blocks, like this:
The main syntactic difference between HLTeX and LaTeX is that HLTeX uses indentation-based environments, like this:
```
\eq:
    f(x) = x^2 + 3
```
Notice that there isn't a trailing `\\end{eq}`!
This makes typing out your documents a breeze.

Commands can take both *required* and *optional* arguments.
Required arguments are enclosed in curly braces `{}`, while optional arguments are enclosed in square brackets `[]`.
For compatibility reasons, only curly braces are required to match;
this means `\\command{[}` is valid HLTeX, because it is valid LaTeX.

As in LaTeX, files are broken into two parts: a *preamble*, and a *document*.
Whereas LaTeX encloses the document in an enormous pair of begin/end commands, in the interest of conciseness,
HLTeX separates these two parts by `===` (or optionally more equals signs, but at least three).
In the preamble, only commands and their arguments are allowed--in particular, this means
environments can only be created in the document (i.e. after the `===`).
