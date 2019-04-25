# tikzpdf

a python script to build/rebuild tikzpicture files for faster developement

*usage* (see `examples`):

    python3 tikzpdf.py -wv test.tikz -p preamble.tex

This takes a `tizkpicture`:
```
\begin{tikzpicture}
  \draw (0,0) circle (2cm);
  \node at (0,0) {Test};
\end{tikzpicture}
```
wraps it in a a LaTeX preview (adding additional preamble from `preamble.tex`):
```
\documentclass{article}
\usepackage{tikz}
\usetikzlibrary{3d}
\usetikzlibrary{calc,positioning}
\usepackage{pgfplots}
\pagestyle{empty}
\usepackage[active,tightpage]{preview}
\PreviewEnvironment[]{tikzpicture}
\usepackage[T1]{fontenc}
% PREAMBLE here
\begin{document}
    % TIKZ picture here
\end{document}
```
and makes a `.pdf` file.

## Help

```
usage: tikzpdf.py [-h] [-p preamble.tex] [-w] [-v] [--viewer VIEWER]
                   example.tikz

tikzpdf.py - a script for tikz picture development

positional arguments:
  example.tikz          tikz file

optional arguments:
  -h, --help            show this help message and exit
  -p preamble.tex, --preamble preamble.tex
                        latex preamble
  -w, --watch           recompile on change
  -v, --view            open viewer
  --viewer VIEWER       viewer executable
```

## Other tools
    - This is inspired by https://github.com/jeroenjanssens/tikz2pdf , which has many more features.  This project is a simplification, clean-up, and rewrite.

## what may go wrong

    - The viewer default is `open` (on a mac)
    - The latex build system is `latexmk`
