# -*- coding: utf-8 -*-

import re
import string


def to_re_pattern(chars="", words=[], single=False):
    if chars:
        return re.compile(r"^[{}]{}$".format(chars, "" if single else "+"))
    elif words:
        return re.compile(r"^({})$".format("|".join(words)))
    return None


PATTERN_WHITESPACE = to_re_pattern(string.whitespace)
PATTERN_SYMBOL     = to_re_pattern(string.ascii_letters + string.digits)
PATTERN_NUMBER     = to_re_pattern(string.digits)
PATTERN_OPERATOR   = to_re_pattern(r"\+\-\*/\<\>=&%", single=True)
PATTERN_CONTROL    = to_re_pattern(r"\{\[\(\)\]\};", single=True)

PATTERNS = [
    PATTERN_SYMBOL,
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


class Symbol(object):
    def __init__(self, name, position):
        self.name = name
        self.position = position    # position in input stream

    def __str__(self):
        return self.name


class Scanner(object):
    def __init__(self):
        self.fname = ""
        self.text = ""
        self.pos = 0

    def parse_file(self, fname):
        self.fname = fname
        with open(fname, "r") as f:
            self.text = f.read()
        return self._parse()

    def _parse(self):
        self.pos = 0
        symbols = []
        while not self._eof():
            s = self._read_symbol()
            if s:
                symbols.append(s)
                print(str(s), end=", ")
        print()
        return symbols

    def _read_symbol(self):
        startpos = self.pos
        word = ""
        pattern = None
        c = self._read_char()

        if c:
            pattern = categorize_word(c)
            if not pattern:
                print("Error: Unknown character: " + c)
                return None
        else:
            return None

        while c and pattern.match(word + c):
            # Handle \n as it isn't picked up by regex apparently
            if not PATTERN_WHITESPACE.match(c):
                word += c
                pattern = categorize_word(word)
            c = self._read_char(False)

        if not self._eof():
            self.pos -= 1

        return Symbol(word, startpos)

    def _read_char(self, skipws=True):
        if self._eof():
            return None

        while skipws and PATTERN_WHITESPACE.match(self.text[self.pos]):
            self.pos += 1
            if self._eof():
                return None

        self.pos += 1
        return self.text[self.pos - 1]

    def _eof(self):
        return self.pos >= len(self.text)
