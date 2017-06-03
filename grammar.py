# -*- coding: utf-8 -*-

# a + b;
# a + (b - c);
# (a + b) * (c - d) / x;

FINAL_STATE = "program"

RULES = [
    # ( "mult", [
    #     "expr * expr".split(),
    # ]),
    #
    # ( "div", [
    #     "expr / expr".split(),
    # ]),
    #
    # ( "add", [
    #     "expr + expr".split(),
    # ]),
    #
    # ( "sub", [
    #     "expr - expr".split(),
    # ]),

    # ( "expr", [
    #     [ "id" ],
    #     [ "literal" ],
    #     [ "mult" ],
    #     [ "div" ],
    #     [ "add" ],
    #     [ "sub" ],
    #     "( expr )".split(),
    # ]),

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
        # "statement statement_list".split(),
        # "statement_list statement_list".split(),
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
    "id",
    "literal",
]


class Token(object):
    def __init__(self, name, tokens=[]):
        self.name = name
        self.tokens = tokens

    def __str__(self):
        return self.name


def requires_rule(rule, subrule):
    """Returns true if a certain subrule is referenced by another rule.

    rule must be the rule array (e.g. as returned by find_rule).
    subrule is the name of the rule to search.
    """
    for i in rule:
        if subrule in i:
            return True
    return False


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


# def match(tokens, rule):
#     """Checks if a token stream matches a rule.
#
#     Returns 0 if it doesn't match, 1 if it matches the begin, and 2 if it
#     matches entirely.
#     """
#     for r in rule:
#         if len(tokens) > len(r):
#             continue
#         for i in range(len(tokens)):
#             if str(tokens[i]) != r[i]:
#                 break
#         else:   # executed if the loop ends without break
#             return 2 if len(tokens) == len(r) else 1
#     return 0
#
# def get_matching(tokens, rules=RULES):
#     """Takes a list of tokens and returns all rules beginning with these tokens"""
#     return { k: v for k,v in rules.items() if match(tokens, v) }
#
# def get_full_matches(tokens, rules=RULES):
#     """Returns a list of rule names that completely match the token stream."""
#     return [ k for k,v in rules.items() if match(tokens, v) == 2 ]
#

# RULES = {
#     "program": [
#         [ "statement_list" ],
#     ],
#     "statement_list": [
#         [ "statement" ],
#         "statement statement_list".split(),
#     ],
#     "statement": [
#         "expr ;".split(),
#         [ ";" ],
#     ],
#     "expr": [
#         [ "id" ],
#         [ "literal" ],
#         [ "mult" ],
#         [ "div" ],
#         [ "add" ],
#         [ "sub" ],
#         "( expr )".split(),
#     ],
#     "mult": [
#         "expr * expr".split(),
#     ],
#     "div": [
#         "expr / expr".split(),
#     ],
#     "add": [
#         "expr + expr".split(),
#     ],
#     "sub": [
#         "expr - expr".split(),
#     ],
# }
