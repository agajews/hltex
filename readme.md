# HLTeX
HLTeX is a new typesetting language built on top of LaTeX designed for conciseness and ease of use,
while also adding support for additional features like inline Matplotlib figure generation, python scripting, 
and SymPy integration.

For integration with Overleaf, see [hltex-chrome](https://github.com/agajews/hltex-overleaf).

### Installation
1. Install the compiler with `pip3 install hltex`.

### Example
Basic features:
```TeX
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

This renders into proper LaTeX:
```TeX
\documentclass{article}
\title{My First Document}
\author{Your Truly}
\begin{document}
\section{HLTeX is Awesome}
Here are some words that are in this section.
Math is fun, so here's an equation:
\begin{equation}
    f(x) = x^2 + 3
\end{equation}
We might want to give our equation a label, like this:
\begin{equation}\label{eq:cubic}
    f(x) = x^3 - 4x^2 + 2
\end{equation}
We can reference our equation with Equation \ref{eq:cubic}.
This is automatically joined with the non-breaking space \verb{~}.
\end{document}
```

See [Syntax](#syntax) and [Advanced Features](#advanced-features) for details.


### Usage
To compile a file into LaTeX, you can use our CLI utility, like this:
```
hltex myfile.hltex
```
By default, this will put the resulting LaTeX code into a file called `myfile.tex`, at which point you can run
```
pdflatex myfile.tex
```
to generate a PDF.
Optionally, you can specify your own output file, like this:
```
hltex myfile.hltex --out myotherfile.tex
```


### Syntax
HLTeX supports two kinds of macros: *commands* and *environments*.

Commands are just as they are in plain LaTeX, and they look like this:
```
This text \emph{is emphasized} using the `emph' command.
```
They are preceeded by a backslash, the *escape character*, followed by either any number of letters in the alphabet
(capital or lowercase), or by a single non-alphabetical character, like this:
```
Once upon a time, in a distant galaxy called \"O\"o\c c, there lived a computer named R.~J. Drofnats.
```
The `\"` *control symbol* puts an umlaut over the following character, while the `\c` control symbol
puts a "cedilla" under the next character.

Environments are slightly different in HLTeX than in LaTeX.
Whereas in LaTeX they are enclosed by begin/end commands, in HLTeX environments use indentation-based blocks, like this:
The main syntactic difference between HLTeX and LaTeX is that HLTeX uses indentation-based environments, like this:
```
\eq:
    f(x) = x^2 + 3
```
Notice that there isn't a trailing `\end{eq}`!
This makes typing out your documents a breeze.

Commands can take both *required* and *optional* arguments.
Required arguments are enclosed in curly braces `{}`, while optional arguments are enclosed in square brackets `[]`.
For compatibility reasons, only curly braces are required to match;
this means `\command{[}` is valid HLTeX, because it is valid LaTeX.

As in LaTeX, files are broken into two parts: a *preamble*, and a *document*.
Whereas LaTeX encloses the document in an enormous pair of begin/end commands, in the interest of conciseness,
HLTeX separates these two parts by `===` (or optionally more equals signs, but at least three).
In the preamble, only commands and their arguments are allowed--in particular, this means
environments can only be created in the document (i.e. after the `===`).


### Advanced Features

#### Inline Matplotlib

1. Install and launch [Docker](https://www.docker.com/).
1. Run `docker pull czentye/matplotlib-minimal`.

[example coming]


#### Inline-python support
We use [Epicbox](https://github.com/StepicOrg/epicbox) and [Docker](https://hub.docker.com/). After installing Docker, run

```
pip install epicbox
docker pull python:3.6.5-alpine
```

Now you can run python code in HLTeX and have save its output directly to your generated LaTeX file!

[example coming]


### Development

To install locally, clone this repo and run `pip install -e PATH_TO_REPO.` You may need sudo permissions.

Test documentation and contribution guidelines incoming.

