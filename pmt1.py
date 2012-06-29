from pymeta.grammar import OMeta
from pymeta.runtime import ParseError

definition = """
hexDigit = (digit|"a"|"b"|"c"|"d"|"e"|"f")
hexInt = "0x" hexDigit+:ds                      -> int(''.join(ds), 16)

octDigit = ("0"|"1"|"2"|"3"|"4"|"5"|"6"|"7")
octInt = "0" octDigit+:ds                       -> int(''.join(ds), 8)

decInt = digit+:ds                              -> int(''.join(ds), 10)

grammar = (hexInt | octInt | decInt):v end      -> v
"""

Grammar = OMeta.makeGrammar(definition, {})

while True:
    text = raw_input("Enter some text to parse: ")
    try:
        print Grammar.parse(text)
    except ParseError, e:
        print e
