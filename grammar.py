# -*- coding: utf-8 -*-

import logging
import string
import re


def to_regex(chars="", words=[], single=False):
    if chars:
        return re.compile(r"^[{}]{}$".format(re.escape(chars), "" if single else "+"))
    elif words:
        return re.compile(r"^({})$".format("|".join([ re.escape(i) for i in words ])))
    return None


FINAL_STATE = "program"

RULES = [
    ( "expr", [
        "expr + term".split(),
        "expr - term".split(),
        [ "term" ]
    ]),

    ( "term", [
        "term * factor".split(),
        "term / factor".split(),
        [ "factor" ],
    ]),

    ( "factor", [
        [ "id" ],
        [ "literal" ],
        "( expr )".split(),
    ]),

    ( "statement", [
        "expr ;".split(),
        [ ";" ],
    ]),

    ( "statement_list", [
        [ "statement" ],
        "statement_list statement".split(),
    ]),

    ( "function", [
        "id ( ) { statement_list }".split(),
    ]),

    ( FINAL_STATE, [
        [ "statement" ],
        [ "function" ],
    ]),
]

TERMINALS = [
    ( "literal",  to_regex(chars=string.digits) ),
    ( "id",       to_regex(chars=string.ascii_letters + string.digits + "_") ),
    ( "operator", to_regex(words="+ - * / % = < > == && ||".split(), single=True) ),
    ( "control",  to_regex(chars="{()};", single=True) ),
]

WHITESPACE = to_regex(chars=string.whitespace)


class Token(object):
    def __init__(self, lexeme, ttype="", position=-1, tokens=[]):
        self.lexeme = lexeme
        self.type = ttype if ttype else lexeme
        self.tokens = tokens

        if position == -1 and tokens:
            self.position = tokens[0].position  # position in input stream
        else:
            self.position = position

    def print(self, depth = 0):
        logging.info(" " * depth + str(self))
        for i in self.tokens:
            i.print(depth + 1)

    def _simplify(self):
        # strip control chars
        self.tokens = [ i for i in self.tokens if i.type != "control" ]

        while len(self.tokens) == 1:
            self._clone(self.tokens[0])

        for i in self.tokens:
            i._simplify()

    def _clone(self, token):
        self.lexeme = token.lexeme
        self.type = token.type
        self.tokens = token.tokens
        self.position = token.position

    def bnf(self):
        if self.type in ("operator", "control"):
            return self.lexeme
        return self.type

    def __str__(self):
        if self.type in ("id", "literal"):
            return "{} ({})".format(self.lexeme, self.type)
        return self.bnf()


# rule functions
def find_rule(name, rules=RULES):
    for i in rules:
        if i[0] == name:
            return i
    return None

def match(tokens, rule):
    """Checks if a token stream matches a rule.

    Expects the rule part of the rule tuple (rule[1]).
    Returns 0 if it doesn't match, 1 if it matches the begin, and 2 if it
    matches entirely.
    """
    for r in rule:
        if len(tokens) > len(r):
            continue
        for i in range(len(tokens)):
            if not tokens[i] or tokens[i].bnf() != r[i]:
                break
        else:   # executed if the loop ends without break
            return 2 if len(tokens) == len(r) else 1
    return 0

def get_matching(tokens, rules=RULES):
    """Takes a list of tokens and returns all rules beginning with these tokens.
    
    Expects a list of rule tuples.
    """
    return [ i for i in rules if match(tokens, i[1]) ]

def get_full_matches(tokens, rules=RULES):
    """Returns a list of rule names that completely match the token stream.
    
    Expects a list of rule tuples.
    """
    return [ i[0] for i in rules if match(tokens, i[1]) == 2 ]


# terminal functions
def categorize_word(word):
    for i in TERMINALS:
        if i[1].match(word):
            return i
    return None
