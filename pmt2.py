from pymeta.grammar import OMeta
from pymeta.runtime import ParseError

from PySide import QtCore

import sys


definition = """
name = (letter | "_"):c (letterOrDigit | "_" | "-")*:cs     -> c + ''.join(cs)
ls = (" " | "\t")*

header = ls name:k ls ":" ls (~"\n" anything)*:cs           -> (k, ''.join(cs))
header_line = header:h "\n"                                 -> h
headers = header_line*:hs                                    -> hs

integer = digit+:ds                                  -> int(''.join(ds), 10)
word_string = (~' ' anything)*:w                     -> ''.join(w)
rect = "rect" ls tuple4:t                             -> QRect(*t)
shape = rect
float = (digit+ "." digit+):f                      -> float(''.join(f))
tuple2 = "(" ls float:a ls float:b ls ")"              -> (a, b)
tuple4 = "(" ls float:a ls float:b ls float:c ls float:d ls ")"
  -> (a, b, c, d)

rule = integer:k ls word_string:l ls shape:s
  -> {'keycode': k, 'label': l, 'shape': s}
rule_line = rule:r "\n"                                   -> r
rules = rule_line*:rs                                    -> rs

grammar = headers:hs "\n" rules:rs spaces end                  -> (hs, rs)
"""


def preprocess(src):
    class ReaderIter(object):
        def __init__(self, src):
            self.i = iter(src)
            self.lineno = 0
            self.col = 0
            self.c = None

        def next(self):
            if '\n' == self.c:
                self.lineno += 1
                self.col = 0
            else:
                self.col += 1

            self.c = self.i.next()

            return self.c

        def skip_until_eol(self):
            while '\n' != self.c:
                self.c = self.i.next()

        def __iter__(self):
            return self

    rd = ReaderIter(src)
    inside_string = False

    while True:
        c = rd.next()

        if '\\' == c:
            yield rd.next()
        elif '"' == c:
            inside_string = not inside_string
            yield c
        elif inside_string:
            yield c
        elif '#' == c:
            if rd.col != 0:
                yield '\n'
            rd.skip_until_eol()
        else:
            yield c


Grammar = OMeta.makeGrammar(definition, {'QRect': QtCore.QRect})


try:
    buf = ''.join(preprocess(sys.stdin.read()))
    print buf
    print '*' * 20
    print repr(Grammar.parse(buf))
except ParseError, e:
    print e
