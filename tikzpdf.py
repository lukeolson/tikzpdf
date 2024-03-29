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

import re


class tikz(object):
    def __init__(self, tikzfile, preamblefile, datafile, watch, view, viewer):
        self.tikzfile = tikzfile
        self.preamblefile = preamblefile
        self.pdffile = os.path.splitext(tikzfile)[0] + '.pdf'
        self.view = view
        self.viewer = viewer

        self.tikzpicture = ''
        self.preamble = ''
        self.datafiles = []
        self.inputfiles = []

        if datafile is not None:
            try:
                with open(datafile, 'r') as f:
                    d = f.read().strip().split('\n')
                d = [dd.strip() for dd in d]
            except:
                print('missing data file')
            self.datafiles += d

        self.compile()

        if watch:
            files = [self.tikzfile]
            if preamblefile is not None:
                files.append(self.preamblefile)
            watcher = Watcher(files, self.compile)
            watcher.watch()

    def reset_data(self):
        self.tikzpicture = ''
        self.preamble = ''
        self.datafiles = []
        self.inputfiles = []

    def read_tikz(self):
        with open(self.tikzfile, 'r') as f:
            self.tikzpicture = f.read()

    def check_tikz_for_extras(self):
        r"""
        Check for
        %\usetikzlibrary{calc,decorations.pathreplacing,shapes.misc}
        at the start of the line
        """
        if not self.tikzpicture:
            return

        c = re.compile(r'^%(\\usetikzlibrary|\\usepackage|\\newcommand|\\renewcommand|\\pgfplotsset)')
        tikz = self.tikzpicture.split('\n')
        for t in tikz:
            result = c.match(t)
            if result:
                self.preamble += t[1:] + '\n'

    def check_tikz_for_extrafiles(self):
        r"""
        check for
        %extra: somefile.dat
        at the start of the line
        this will copy the data file into the compile directory
        %extra: somefile.dat, somepath/somefile.dat
        will copy the file somefile.dat to somepath/somefile.dat in the build directory
        """
        newdatafiles = []
        if not self.tikzpicture:
            return

        c1 = re.compile(r'^%extra:(.*),(.*)')
        c2 = re.compile(r'^%extra:(.*)')
        tikz = self.tikzpicture.split('\n')
        for t in tikz:
            result = c1.match(t)
            if not result:
                result = c2.match(t)
            if result:
                filename = result.group(1).strip()
                if len(result.groups())>1:
                    newfilename = result.group(2).strip()
                    newdatafiles.append((filename, newfilename))
                else:
                    newdatafiles.append(filename)
                if not os.path.isfile(filename):
                    raise ValueError(f'Expecting only filenames... ({filename})')
        self.datafiles += newdatafiles

    def check_tikz_for_input(self):
        r"""
        check for
        %\input{something}
        at the start of the line

        Since nesting inputs will not work, we look for this input in the comments.

        assumes one per \input
        assumes no subdirectory
        """
        newdatafiles = []
        if not self.tikzpicture:
            return

        c = re.compile(r'^%\\input{(.*)}')
        tikz = self.tikzpicture.split('\n')
        for t in tikz:
            result = c.match(t)
            if(result):
                filename = result.group(1)
                if '/' in filename:
                    raise ValueError('Expecting only filenames...')
                if ',' in filename:
                    raise ValueError('Expecting only one filename...')
                newdatafiles.append(filename.strip())
                self.preamble += result.group(0)[1:]
        self.datafiles += newdatafiles

    def read_preamble(self):
        if self.preamblefile is not None:
            with open(self.preamblefile, 'r') as f:
                self.preamble += f.read()

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
        self.reset_data()
        self.read_tikz()
        self.check_tikz_for_extras()
        self.check_tikz_for_input()
        self.check_tikz_for_extrafiles()
        self.read_preamble()
        self.set_latex()

        with tempfile.TemporaryDirectory() as d:
            texfile = os.path.join(d, "tikz.tex")

            # write latex
            with open(texfile, "w") as f:
                f.write(self.latex)

            # copy data
            for f in self.datafiles:
                if type(f) == tuple:
                    os.makedirs(os.path.join(d,os.path.dirname(f[1])), exist_ok=True)
                    shutil.copy(f[0], os.path.join(d, f[1]), follow_symlinks=True)
                else:
                    shutil.copy(f, os.path.join(d, f), follow_symlinks=True)

            # compile latex
            output = subprocess.call(["ls", "-l", d])
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
            notfound = True
            while notfound:
                try:
                    stamp = os.stat(self.filenames[i]).st_mtime
                    notfound = False
                except FileNotFoundError:
                    print('attempting to find')
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
