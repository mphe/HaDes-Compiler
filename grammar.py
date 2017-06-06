# -*- coding: utf-8 -*-

import logging
import string

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

# TERMINALS = [
#     ( "literal", string.digits ),
#     ( "id", string.ascii_letters + string.digits + "_" ),
#     ( "operator", "+ - * / % = < > == && ||".split() ),
#     ( "control", "{()};" ),
# ]
#
# WHITESPACE = string.whitespace


class Token(object):
    def __init__(self, name, tokens=[]):
        self.name = name
        self.tokens = tokens

    def print(self, depth = 0):
        logging.info(" " * depth + self.name)
        for i in self.tokens:
            i.print(depth + 1)

    def _simplify(self):
        while len(self.tokens) == 1:
            self.name = self.tokens[0].name
            self.tokens = self.tokens[0].tokens

        for i in self.tokens:
            i._simplify()

    def __str__(self):
        return self.name


def find_rule(name, rules=RULES):
    for i in rules:
        if i[0] == name:
            return i
    return None

def match(tokens, rule):
    """Checks if a token stream matches a rule.

    Returns 0 if it doesn't match, 1 if it matches the begin, and 2 if it
    matches entirely.
    """
    for r in rule:
        if len(tokens) > len(r):
            continue
        for i in range(len(tokens)):
            if str(tokens[i]) != r[i]:
                break
        else:   # executed if the loop ends without break
            return 2 if len(tokens) == len(r) else 1
    return 0

def get_matching(tokens, rules=RULES):
    """Takes a list of tokens and returns all rules beginning with these tokens"""
    return [ i for i in rules if match(tokens, i[1]) ]

def get_full_matches(tokens, rules=RULES):
    """Returns a list of rule names that completely match the token stream."""
    return [ i[0] for i in rules if match(tokens, i[1]) == 2 ]
