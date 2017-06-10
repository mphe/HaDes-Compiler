# -*- coding: utf-8 -*-

import grammar

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
        symbol = None
        c = self._read_char()

        if c:
            symbol = grammar.categorize_word(c)
            if not symbol:
                print("Error: Unknown symbol: " + c)
                return None
        else:
            return None

        while c and symbol[1].match(word + c):
            # Handle \n as it isn't picked up by regex apparently
            # NOTE: Code changed since then, might need to test again to see
            #       if this is still necessary
            if not grammar.WHITESPACE.match(c):
                word += c
                symbol = grammar.categorize_word(word)
            c = self._read_char(False)

        if not self._eof():
            self.pos -= 1

        return grammar.Token(
            word, symbol[0], position=startpos)

    def _read_char(self, skipws=True):
        if self._eof():
            return None

        while skipws and grammar.WHITESPACE.match(self.text[self.pos]):
            self.pos += 1
            if self._eof():
                return None

        self.pos += 1
        return self.text[self.pos - 1]

    def _eof(self):
        return self.pos >= len(self.text)
