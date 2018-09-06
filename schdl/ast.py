from abc import ABC
from types import MethodType
from collections import deque


class Coordinate:
    def __init__(self, filename, line, column, source):
        self.filename = filename
        self.line = line
        self.column = column
        self.source = source

    def __str__(self):
        return ':'.join(map(str, (self.filename, self.line, self.column)))


class CoordinatedError(Exception):
    """
    Exception with coordinate information.
    """
    def __init__(self, *args, coord=None, **kwargs):
        self.coord = coord
        super().__init__(self, *args, **kwargs)

    def __str__(self):
        line = self.coord.source.splitlines()[self.coord.line - 1]
        return "{}: {}:\n    {}\n    {}^".format(
            self.coord, super().__str__(), line, ' ' * self.coord.column)


class ASTElement(ABC):
    """
    Decorator for classes to provide coordinates.
    """
    def __new__(cls, wcls):
        """
        .. note:: This is called when *wrapping* a class.
        """
        if wcls.__new__ is not object.__new__:
            orig_new = wcls.__new__

            def new_wrapper(cls, *args, coord=None, **kwargs):
                obj = orig_new(cls, *args, **kwargs)
                obj.coord = coord
                return obj

            wcls.__new__ = new_wrapper

        if wcls.__init__ is not object.__init__:
            orig_init = wcls.__init__

            def init_wrapper(self, *args, coord=None, **kwargs):
                self.coord = coord
                init_meth = MethodType(orig_init, self)
                init_meth(*args, **kwargs)

            wcls.__init__ = init_wrapper

        return cls.register(wcls)


@ASTElement
class SExpression(deque):
    def __repr__(self):
        return '({})'.format(' '.join(map(repr, self)))


@ASTElement
class Quoted:
    """
    A simple wrapper for a quoted element in the abstract syntax tree.
    """
    def __init__(self, elem):
        self.elem = elem

    def __repr__(self):
        return "'{!r}".format(self.elem)


@ASTElement
class Symbol(str):
    """
    A type for symbols, like a ``str``, but alternate representation.
    """
    def __repr__(self):
        return str(self)


@ASTElement
class Float(float):
    pass


@ASTElement
class Integer(int):
    pass
