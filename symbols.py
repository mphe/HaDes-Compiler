# -*- coding: utf-8 -*-

import re
import string


def to_re_pattern(chars="", words=[], single=False):
    if chars:
        return re.compile(r"^[{}]{}$".format(re.escape(chars), "" if single else "+"))
    elif words:
        return re.compile(r"^({})$".format(re.escape("|".join(words))))
    return None


PATTERN_WHITESPACE = to_re_pattern(string.whitespace)
PATTERN_IDENTIFIER = to_re_pattern(string.ascii_letters + string.digits)
PATTERN_NUMBER     = to_re_pattern(string.digits)
PATTERN_OPERATOR   = to_re_pattern("+-*/<>=&%", single=True)
PATTERN_CONTROL    = to_re_pattern("{()};", single=True)

PATTERNS = [
    PATTERN_IDENTIFIER,
    PATTERN_NUMBER,
    PATTERN_OPERATOR,
    PATTERN_CONTROL,
    PATTERN_WHITESPACE,
]


def categorize_word(word):
    for i in PATTERNS:
        if i.match(word):
            return i
    return None


class SymbolType(object):
    Unknown = ""
    Identifier = "id"
    Literal = "literal"
    Expression = "expr"
    Operator = "op"
    Control = "control"
    Function = "function"

    @staticmethod
    def from_pattern(pattern):
        if pattern == PATTERN_IDENTIFIER:
            return SymbolType.Identifier

        elif pattern == PATTERN_NUMBER:
            return SymbolType.Literal

        elif pattern == PATTERN_OPERATOR:
            return SymbolType.Operator

        elif pattern == PATTERN_CONTROL:
            return SymbolType.Control

        else:
            return SymbolType.Unknown


class Symbol(object):
    def __init__(self, name, position, stype):
        self.name = name
        self.position = position    # position in input stream
        self.type = stype

    def __str__(self):
        if self.type in (SymbolType.Operator, SymbolType.Control):
            return self.name
        return self.type
