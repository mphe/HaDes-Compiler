# -*- coding: utf-8 -*-

import symbols
import grammar


class Parser(object):
    def __init__(self):
        self.pos = 0
        self.symbols = []

    def parse_file(self, fname):
        scanner = Scanner()
        self.symbols = scanner.parse_file(fname)
        return self._parse()

    def _parse(self):
        self.pos = 0
        tokens = []
        token = []

        print(", ".join([ str(i) for i in self.symbols ]))

        while True:
            token = self._parse_greedy(token, [ grammar.find_rule("program") ])
            if not token:
                break
            else:
                tokens.append(token)
                token = []
        return grammar.Token("root", tokens)

        # while not self._eof():
        #     token = [ self._parse_tokenstream(token) ]
        #     if token[0] is None:
        #         print("Syntax Error")
        #         return
        #     elif str(token[0]) == "program":
        #         tokens += token
        #         token = []
        #
        # # if grammar.match(tokens, grammar.RULES["program"]):
        # if grammar.match(tokens, grammar.find_rule("program")[1]):
        #     tokens += [ grammar.Token("program", token) ]
        # else:
        #     print("illformed program")
        #     return None
        # return grammar.Token("root", tokens)

    def _parse_greedy(self, tstream, rules=grammar.RULES):
        print("searching greedy: " + ", ".join([ str(i[0]) for i in rules ]))
        print("to complete: " + ", ".join([ str(i) for i in tstream ]))
        token = []  # Always contains 1 token (except here)
        solution = (None, self.pos) # stores a solution and its stream position

        while True:
        # while not self._eof():
            # currentpos = self.pos
            newtoken = self._parse_tokenstream(token)

            if newtoken is None:
                # self.pos = currentpos
                break
            else:
                if token and newtoken is token[0]:
                    print("found endless loop -> break")
                    break

                token = [ newtoken ]
                print("found greedy: " + str(newtoken))

                print("DEBUG:")
                print("searching greedy: " + ", ".join([ str(i[0]) for i in rules ]))
                print("to complete: " + ", ".join([ str(i) for i in tstream ]))
                print("DEBUG END")

                # check if the found token is a solution and update it
                # if grammar.find_rule(str(newtoken), rules):
                if grammar.get_matching(tstream + token, rules):
                    solution = (token, self.pos)
                    print("found solution: " + str(newtoken))

        # print("return greedy: " + str(token[0] if token else None))
        # return token[0] if token else None
        print("return greedy: " + str(solution[0][0] if solution[0] else None))
        self.pos = solution[1]
        return solution[0][0] if solution[0] else None

    def _parse_tokenstream(self, tstream=None):
        print("parse tokenstream: " + ", ".join([ str(t) for t in tstream ]))
        if tstream is None:
            tstream = []

        # print("parsing at: " + str(self.pos) + ", ".join([ str(t) for t in tstream ]))
        while True:
            # eof = self._eof()
            matching = grammar.RULES

            # if not eof:
            while len(matching) > 0:
                tstream.append(self._read_token())
                matching = grammar.get_matching(tstream, matching)

            # print("backpaddling at: " + str(self.pos) + ", ".join([ str(t) for t in tstream ]))

            # At this point nothing matches anymore, so backpaddle
            # while True:
            if True:
                # if not eof:
                tstream.pop()
                self.pos -= 1

                if len(tstream) == 0:
                    print("no matches found")
                    return None

                full = grammar.get_full_matches(tstream)
                m = grammar.get_matching(tstream)

                # print("possible matches:" + ", ".join([ i[0] for i in m ]))
                # print("full matches:" + ", ".join([ i[0] for i in full ]))

                # if len(full) == 1:
                if len(full) > 0:
                    if len(full) > 1:
                        print("ambiguous:")
                        for i in full:
                            print("\t" + str(i))
                        print("using first one")
                        # return None

                    print("found match: " + str(full[0]))
                    for i in tstream:
                        print("\t" + str(i))
                    return grammar.Token(full[0], tstream)

                elif len(full) == 0:
                    print("diverging at " + str(self.pos) + ": " + ", ".join([ str(t) for t in tstream ]))
                    currentpos = self.pos
                    t = self._parse_greedy(tstream, m)
                    if t is None:
                        print("nothing found, return None")
                        self.pos = currentpos
                        return None
                        # continue
                    else:
                        print("found: " + str(t))
                        tstream.append(t)
                        continue   # effectively restarts the function
                        # break   # effectively restarts the function

    def _read_token(self):
        s = None if self._eof() else self.symbols[self.pos]
        self.pos += 1
        return grammar.Token(str(s))

    def _eof(self):
        return self.pos >= len(self.symbols)


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
