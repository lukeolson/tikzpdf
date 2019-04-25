#!/usr/bin/env python

from setuptools import setup

with open('tikzpdf.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = eval(line.split('=')[-1])

long_description = open('README.md', 'r').read()

setup(name='tikzpdf',
      license='MIT',
      version=version,
      description='tikz -> pdf',
      long_description=long_description,
      author='Luke Olson',
      author_email='luke.olson@gmail.com',
      url='https://github.com/lukeolson/tikzpdf',
      py_modules=['tikzpdf'],
      entry_points={'console_scripts': ['tikzpdf = tikzpdf:main']},
      classifiers=['Environment :: Console',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   'Topic :: Utilities'])
