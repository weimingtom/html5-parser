#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: Apache 2.0 Copyright: 2017, Kovid Goyal <kovid at kovidgoyal.net>

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
from functools import partial

import html5lib

import html5_parser

try:
    from time import monotonic
except ImportError:
    from time import time as monotonic

TF = 'test/large.html'
try:
    raw = open(TF, 'rb').read()
except Exception:
    try:
        from urllib.request import urlopen
    except ImportError:
        from urllib import urlopen
    print('Downloading large HTML file...')
    raw = urlopen('https://www.w3.org/TR/html5/single-page.html').read()
    open(TF, 'wb').write(raw)

print('Testing with HTML file of', '{:,}'.format(len(raw)), 'bytes')


def timeit(func, number=1):
    total = 0
    for i in range(number):
        st = monotonic()
        r = func()
        t = monotonic() - st
        total += t
        del r
    return total / number


def doit(name, func, num=20):
    print('Parsing', num, 'times with', name)
    t = timeit(func, num)
    print(name, 'took an average of: {:,.3f} seconds to parse it'.format(t))
    return t


p = argparse.ArgumentParser(description='Benchmark html5-parser')
p.add_argument('treebuilder', nargs='?', default='lxml', choices='lxml soup dom etree'.split())
p.add_argument('--num', '-n', default=20, type=int,
               help='Number of repetitions for html5lib (html5-parser will use 5x as many reps)')
args = p.parse_args()

t1 = doit(
    'html5-parser',
    partial(
        html5_parser.parse,
        raw,
        transport_encoding="utf-8",
        namespace_elements=True,
        treebuilder=args.treebuilder),
    num=args.num * 5)
t2 = doit(
    'html5lib',
    partial(html5lib.parse, raw, transport_encoding="utf-8", treebuilder=args.treebuilder),
    num=args.num)
print('Speedup: {}x'.format(round(t2 / t1)))
