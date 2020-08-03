#!/usr/bin/env python
"""
This script is used to compile a tikzpicture into a pdf
"""

__version__ = '0.1.0'

import argparse
import sys

import os
import sys
import time
import shutil

import tempfile
import subprocess


class tikz(object):
    def __init__(self, tikzfile, preamblefile, datafile, watch, view, viewer):
        self.tikzfile = tikzfile
        self.preamblefile = preamblefile
        self.pdffile = os.path.splitext(tikzfile)[0] + '.pdf'
        self.view = view
        self.viewer = viewer

        self.tikzpicture = ""
        self.preamble = ""

        self.datafiles = []
        if datafile is not None:
            try:
                with open(datafile, 'r') as f:
                    d = f.read().strip().split('\n')
                d = [dd.strip() for dd in d]
            except:
                print('missing data file')
            self.datafiles = d

        self.compile()

        if watch:
            files = [self.tikzfile]
            if preamblefile is not None:
                files.append(self.preamblefile)
            watcher = Watcher(files, self.compile)
            watcher.watch()

    def read_tikz(self):
        with open(self.tikzfile, 'r') as f:
            self.tikzpicture = f.read()

    def read_preamble(self):
        if self.preamblefile is not None:
            with open(self.preamblefile, 'r') as f:
                self.preamble = f.read()

    def set_latex(self):

        self.latex = (r"""
\documentclass{article}
\usepackage{tikz}
\usetikzlibrary{3d}
\usetikzlibrary{calc,positioning}
\usepackage{pgfplots}
\pagestyle{empty}
\usepackage[active,tightpage]{preview}
\renewcommand\PreviewBbAdjust{0bp 0bp 0bp 0bp}
\PreviewEnvironment[]{tikzpicture}
\usepackage[T1]{fontenc}
"""
                      f"{self.preamble}\n"
                      r"\begin{document}"
                      f"{self.tikzpicture}\n"
                      r"""\end{document}""")

    def compile(self):
        self.read_tikz()
        self.read_preamble()
        self.set_latex()

        with tempfile.TemporaryDirectory() as d:
            texfile = os.path.join(d, "tikz.tex")

            # write latex
            with open(texfile, "w") as f:
                f.write(self.latex)

            # copy data
            for f in self.datafiles:
                print(f)
                shutil.copy(f, os.path.join(d, f))

            # compile latex
            output = subprocess.call(["latexmk", "-pdf", "-cd", "-halt-on-error", texfile])

            # copy pdf
            if output == 0:
                subprocess.call(['cp', os.path.join(d, "tikz.pdf"), self.pdffile])

            # open
            if self.view:
                subprocess.call([self.viewer, self.pdffile])


class Watcher(object):
    """
    https://stackoverflow.com/questions/182197/how-do-i-watch-a-file-for-changes/49007649#49007649
    """
    running = True
    refresh_delay_secs = 0.1

    # Constructor
    def __init__(self, watch_files, call_func_on_change=None, *args, **kwargs):
        self._cached_stamps = [0 for w in watch_files]
        self.filenames = watch_files
        self.call_func_on_change = call_func_on_change
        self.args = args
        self.kwargs = kwargs

    # Look for changes
    def look(self):
        for i in range(len(self.filenames)):
            attempt = 0
            while attempt < 5:
                try:
                    stamp = os.stat(self.filenames[i]).st_mtime
                    attempt = 5
                except FileNotFoundError:
                    attempt += 1
            if stamp != self._cached_stamps[i]:
                self._cached_stamps[i] = stamp
                # File has changed, so do something...
                if self.call_func_on_change is not None:
                    self.call_func_on_change(*self.args, **self.kwargs)

    # Keep watching in a loop
    def watch(self):
        while self.running:
            time.sleep(self.refresh_delay_secs)
            self.look()
            try:
                # Look for changes
                time.sleep(self.refresh_delay_secs)
                self.look()
            except KeyboardInterrupt:
                print('\nDone')
                break
            except FileNotFoundError:
                # Action on file not found
                pass
            except:
                print('Unhandled error: %s' % sys.exc_info()[0])


def main():
    parser = argparse.ArgumentParser(description="tikzpdf - a script for tikz picture development")
    parser.add_argument("tikzfile", help="tikz file", metavar="example.tikz")
    parser.add_argument("-p", "--preamble", default=None, help="latex preamble", metavar="preamble.tex")
    parser.add_argument("-d", "--data", default=None, help="additional data files", metavar="data.txt")
    parser.add_argument("-w", "--watch", action="store_true", default=False, help="recompile on change")
    parser.add_argument("-v", "--view", action="store_true", default=False, help="open viewer")
    parser.add_argument("--viewer", default='open', help="viewer executable")

    args = parser.parse_args()

    T = tikz(args.tikzfile, args.preamble, args.data, args.watch, args.view, args.viewer)


if __name__ == "__main__":
    main()
