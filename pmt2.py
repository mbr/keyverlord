from pymeta.grammar import OMetaGrammar
from pymeta.runtime import ParseError

from PySide import QtCore

import sys


# primitives
definition = """
escaped_char = '\\\\' ('"' | '\\\\'):c
  -> c
name = (letter | "_"):c (letterOrDigit | "-")*:cs
  -> c + ''.join(cs)
word_string = (~' ' anything)*:w
  -> ''.join(w)
string = '"' (escaped_char | ~('"') anything)*:cs '"'
  -> ''.join(cs)
any_string = (string | word_string)
basic_int =  digit+:ds
  -> int(''.join(ds), 10)
float = digit+:fs '.' digit+:ss
  -> float(''.join(fs + ['.'] + ss))
eol_string = (~vspace anything)*:cs
  -> ''.join(cs).strip()

tuple2 = '(' hspace* float:a hspace* float:b hspace* ')'
  -> (a, b)
point = tuple2:t
  -> QPointF(*t)
tuple4 = '(' hspace* float:a hspace* float:b hspace*\
         float:c hspace* float:d hspace* ')'
  -> (a, b, c, d)
"""

# shapes
definition += """
rect = "rect" hspace* tuple4:t
  -> QRectF(*t)
shape = rect
"""

# main stuff
definition += """
header_line = hspace* name:k hspace* ':' hspace*\
              (float|basic_int|eol_string):v hspace* vspace
  -> (k, v)
headers = header_line*:hs
  -> dict(hs)

rule = basic_int:k (hspace* ~shape any_string)*:ls hspace* shape:s
  -> Rule(k, ls, s)
row_key = hspace* basic_int:k (hspace* string)+:ls hspace* float?:f
  -> (k, ls, f)
row_rule = "row" hspace* point:rc row_key:k1 (',' row_key)*:ks
  -> RowRule(rc, [k1] + ks)
rule_line = (rule | row_rule):r vspace
  -> r
rules = rule_line*:rs
  -> rs

grammar = headers:hs emptyline rules:rs spaces end
  -> PhysicalKeyboard(hs, rs)
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
            yield '\\'
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


class Rule(object):
    def __init__(self, keycode, labels, shape):
        self.keycode = keycode
        self.labels = labels
        self.shape = shape

    def to_keys(self, kb):
        return [Key(self.keycode, self.labels, self.shape)]

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__,
                                   self.keycode,
                                   self.labels,
                                   self.shape)


class RowRule(object):
    def __init__(self, coords, row_keys):
        self.coords = coords
        self.row_keys = row_keys

    def to_keys(self, kb):
        def_height = kb.get_conf('default-key-height')
        def_width = kb.get_conf('default-key-width')
        def_gap = kb.get_conf('default-key-gap')
        ks = []

        cur_offset = 0
        for i, (keycode, labels, key_width) in enumerate(self.row_keys):
            w = key_width or def_width
            shape = QtCore.QRectF(
                self.coords + QtCore.QPointF(cur_offset, 0),
                QtCore.QSizeF(def_height, w)
            )
            ks.append(Key(keycode, labels, shape))
            cur_offset += def_gap + w
        return ks

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__,
                               self.coords,
                               self.row_keys)


class PhysicalKeyboard(object):
    default_headers = {
        'name': 'Unnamed keyboard',
        'default-key-gap': 0.1,
        'default-key-width': 1.8,
        'default-key-height': 1.8
    }

    def __init__(self, headers, rules):
        self.headers = headers
        self.rules = rules

        self.update_keys()

    def get_conf(self, k):
        try:
            return self.headers[k]
        except KeyError:
            return self.default_headers[k]

    def update_keys(self):
        self.keys = []
        for rule in self.rules:
            self.keys.extend(rule.to_keys(self))

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__,
                               self.headers,
                               self.rules)


class Key(object):
    def __init__(self, keycode, labels, shape):
        self.keycode = keycode
        self.labels = labels
        self.shape = shape

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__,
                                   self.keycode,
                                   self.labels,
                                   self.shape)


Grammar = OMetaGrammar.makeGrammar(definition, {
    'QRectF': QtCore.QRectF,
    'QPointF': QtCore.QPointF,
    'Rule': Rule,
    'RowRule': RowRule,
    'PhysicalKeyboard': PhysicalKeyboard
})


try:
    buf = ''.join(preprocess(sys.stdin.read()))
    print buf
    print '*' * 20
    kb = Grammar.parse(buf)
    print repr(kb)
    print
    for k in kb.keys:
        print k
except ParseError, e:
    print e
