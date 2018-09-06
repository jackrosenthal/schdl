import re
from .ast import (Coordinate, CoordinatedError, SExpression,
                  Quoted, Symbol, Float, Integer)


class ControlToken:
    """
    Base class for all control tokens.
    """
    def __init__(self, coord):
        self.coord = coord

    def __repr__(self):
        return self.__class__.__name__


CT = {k: type(k, (ControlToken, ), dict(ControlToken.__dict__))
      for k in ("(", ")", "'")}

tokens_p = re.compile(r'''
    (?:  (?P<quotefail>'\s+|'\)|';)
    |    (?P<control>\(|\)|')
    |    (?:\s+)
    |    (?:;[^\n]*(?:\n|$))
    |    (?P<float>(?:\d*\.\d+|\d+\.\d*))
    |    (?P<decimal>\d+)
    |    (?P<symbol>[^()"'\s;\d.][^()"'\s;\#]*)
    |    (?P<fail>.)
    )''', re.VERBOSE | re.DOTALL)


def lex(code, filename='input'):
    """
    Lexical analysis: yields tokens
    """
    lines = 1
    coord = Coordinate(filename, lines, 0, code)
    for m in tokens_p.finditer(code):
        if m.group('quotefail') or m.group('fail'):
            raise CoordinatedError("Syntax Error", coord=coord)
        if m.group('control'):
            yield CT[m.group('control')](coord=coord)
        elif m.group('float'):
            yield Float(m.group('float'), coord=coord)
        elif m.group('decimal'):
            yield Integer(m.group('decimal'), coord=coord)
        elif m.group('symbol'):
            yield Symbol(m.group('symbol'), coord=coord)

        # next coordinate computation
        lines_list = m.group(0).splitlines()
        lines += len(lines_list) - 1
        coord = Coordinate(filename, lines, len(lines_list[-1]), code)


def parse(tokens):
    stack = []
    for t in tokens:
        if isinstance(t, CT[')']):
            se = SExpression()
            while True:
                try:
                    itm = stack.pop()
                except IndexError:
                    raise CoordinatedError(
                        "Syntax Error: too many closing parenthesis",
                        coord=t.coord)
                if isinstance(itm, CT['(']):
                    se.coord = itm.coord
                    stack.append(se)
                    break
                else:
                    se.appendleft(itm)
        else:
            stack.append(t)
            if isinstance(t, ControlToken):
                continue
        while len(stack) >= 2 and isinstance(stack[-2], CT["'"]):
            itm = stack.pop()
            stack.pop()
            stack.append(Quoted(itm))
        if len(stack) == 1:
            yield stack.pop()
    if stack:
        raise CoordinatedError("Syntax Error: incomplete parse", coord=t.coord)
