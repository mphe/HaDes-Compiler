# -*- coding: utf-8 -*-

import symbols


class Scanner(object):
    def __init__(self):
        self.text = ""
        self.pos = 0

    def parse_file(self, fname):
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
        return symbols

    def _read_symbol(self):
        startpos = self.pos
        word = ""
        pattern = None
        c = self._read_char()

        if c:
            pattern = symbols.categorize_word(c)
            if not pattern:
                print("Error: Unknown character: " + c)
                return None
        else:
            return None

        while c and pattern.match(word + c):
            # Handle \n as it isn't picked up by regex apparently
            if not symbols.PATTERN_WHITESPACE.match(c):
                word += c
                pattern = symbols.categorize_word(word)
            c = self._read_char(False)

        if not self._eof():
            self.pos -= 1

        return symbols.Symbol(
            word, startpos, symbols.SymbolType.from_pattern(pattern))

    def _read_char(self, skipws=True):
        if self._eof():
            return None

        while skipws and symbols.PATTERN_WHITESPACE.match(self.text[self.pos]):
            self.pos += 1
            if self._eof():
                return None

        self.pos += 1
        return self.text[self.pos - 1]

    def _eof(self):
        return self.pos >= len(self.text)
