# -*- coding: utf-8 -*-

import grammar

class Scanner(object):
    def __init__(self):
        self.text = ""
        self.posinfo = grammar.Position()

    def parse_file(self, fname):
        with open(fname, "r") as f:
            self.text = f.read()
        return self._parse()

    def _parse(self):
        self.posinfo = grammar.Position(0, 0, 0)
        symbols = []
        while not self._eof():
            s = self._read_symbol()
            if s:
                symbols.append(s)
        return symbols

    def _read_symbol(self):
        startpos = self.posinfo.clone()
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

        lastposinfo = self.posinfo.clone()  # used to restore position afterwards
        while c and symbol[1].match(word + c):
            # Handle \n as it isn't picked up by regex apparently
            # NOTE: Code changed since then, might need to test again to see
            #       if this is still necessary
            if not grammar.WHITESPACE.match(c):
                word += c
                symbol = grammar.categorize_word(word)
            lastposinfo = self.posinfo.clone()
            c = self._read_char(False)

        if not self._eof():
            self.posinfo = lastposinfo

        return grammar.Token(word, symbol[0], position=startpos)

    def _read_char(self, skipws=True):
        if self._eof():
            return None

        while skipws and grammar.WHITESPACE.match(self.text[self.posinfo.pos]):
            self._advance()
            if self._eof():
                return None

        self._advance()
        return self.text[self.posinfo.pos - 1]

    def _advance(self):
        if self.text[self.posinfo.pos] == "\n":
            self.posinfo.new_line()
        else:
            self.posinfo.increase()

    def _eof(self):
        return self.posinfo.pos >= len(self.text)
