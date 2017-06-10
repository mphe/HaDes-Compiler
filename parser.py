# -*- coding: utf-8 -*-

import scanner
import grammar
import logging


def str_list(l):
    return ", ".join([ i.bnf() for i in l ])


class Parser(object):
    def __init__(self):
        self.pos = 0
        self.symbols = []

    def parse_file(self, fname):
        s = scanner.Scanner()
        self.symbols = s.parse_file(fname)
        return self._parse()

    def _parse(self):
        self.pos = 0
        program = []
        token = None

        logging.debug("Symbol stream: " + str_list(self.symbols))

        while True:
            token = self._parse_greedy(rules=[ grammar.find_rule("program") ])
            if not token:
                if self._eof():
                    break
                else:
                    logging.error("Syntax Error")
                    return None
            else:
                program.append(token)

        out = grammar.Token("root", tokens=program)
        out._simplify()
        return out

    def _parse_greedy(self, tstream=None, rules=grammar.RULES):
        if tstream is None:
            tstream = []

        logging.debug("searching greedy at {!s}: {}".format(self.pos, ", ".join([ i[0] for i in rules ])))
        logging.debug("to complete: " + str_list(tstream))
        token = []  # Always contains 1 token (except here)
        solution = (None, self.pos) # stores a solution and its stream position

        while True:
            logging.debug("parse tokenstream: " + str_list(token))
            newtoken = self._parse_tokenstream(token)

            if newtoken is None:
                break
            else:
                if token and newtoken is token[0]:
                    logging.debug("found endless loop -> break")
                    break

                token = [ newtoken ]

                # check if the found token is a solution and update it
                if grammar.get_matching(tstream + token, rules):
                    solution = (newtoken, self.pos)
                    logging.debug("found solution: " + newtoken.bnf())
                else:
                    logging.debug("found greedy (but not a solution): " + newtoken.bnf())
                    logging.debug("\tintial search constraints:")
                    logging.debug("\t\tsearching greedy: " + ", ".join([ i[0] for i in rules ]))
                    logging.debug("\t\tto complete: " + str_list(tstream))

        logging.debug("return greedy: " + (solution[0].bnf() if solution[0] else "None"))
        self.pos = solution[1]
        return solution[0]

    def _parse_tokenstream(self, tstream=None):
        if tstream is None:
            tstream = []

        while True:
            matching = grammar.RULES

            while len(matching) > 0:
                tstream.append(self._read_token())
                matching = grammar.get_matching(tstream, matching)

            # At this point nothing matches anymore, so backpaddle
            tstream.pop()
            self.pos -= 1

            if len(tstream) == 0:
                logging.debug("\tno matches found")
                return None

            full = grammar.get_full_matches(tstream)
            if len(full) > 0:
                if len(full) > 1:
                    logging.debug("\tambiguous:")
                    for i in full:
                        logging.debug("\t\t" + i)
                    logging.debug("\tusing first one")

                logging.debug("\tfound match: " + full[0])
                for i in tstream:
                    logging.debug("\t\t" + i.bnf())
                return grammar.Token(full[0], tokens=tstream)

            elif len(full) == 0:
                t = self._parse_greedy(tstream, grammar.get_matching(tstream))
                if t is None:
                    logging.debug("\tnothing found, return None")
                    return None
                else:
                    logging.debug("\tfound: " + t.bnf())
                    tstream.append(t)
                    continue   # effectively restarts the function

    def _read_token(self):
        s = None if self._eof() or self.pos < 0 else self.symbols[self.pos]
        self.pos += 1
        return s

    def _eof(self):
        return self.pos >= len(self.symbols)
