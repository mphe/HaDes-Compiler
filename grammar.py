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
    ( "statement", [
        "if ( expr ) statement".split(),
        "if ( expr ) statement else statement".split(),
        "while ( expr ) statement".split(),
        "return expr ;".split(),
        "break ;".split(),
        "continue ;".split(),
        "expr ;".split(),
        "{ statement_list }".split(),
        [ ";" ],
    ]),

    ( "statement_list", [
        [ "statement" ],
        "statement_list statement".split(),
    ]),

    ( "function", [
        "def id ( ) statement".split(),
        "def id ( param_list ) statement".split(),
    ]),

    ( FINAL_STATE, [
        [ "statement" ],
        [ "function" ],
    ]),

    ( "expr", [
        [ "expr_assignment" ],
    ]),

    ( "expr_assignment", [
        "id = expr_logic_or".split(),
        [ "expr_logic_or" ],
    ]),

    ( "expr_logic_or", [
        "expr_logic_or || expr_logic_and".split(),
        [ "expr_logic_and" ],
    ]),

    ( "expr_logic_and", [
        "expr_logic_and && expr_bitwise".split(),
        [ "expr_bitwise" ],
    ]),

    ( "expr_bitwise", [
        "expr_bitwise & expr_compare".split(),
        "expr_bitwise ^ expr_compare".split(),
        "expr_bitwise | expr_compare".split(),
        [ "expr_compare" ],
    ]),

    ( "expr_compare", [
        "expr_compare == expr_shift".split(),
        "expr_compare != expr_shift".split(),
        "expr_compare < expr_shift".split(),
        "expr_compare > expr_shift".split(),
        "expr_compare <= expr_shift".split(),
        "expr_compare >= expr_shift".split(),
        [ "expr_shift" ],
    ]),

    ( "expr_shift", [
        "expr_shift << expr_sum".split(),
        "expr_shift >> expr_sum".split(),
        "expr_shift <<< expr_sum".split(),
        "expr_shift >>> expr_sum".split(),
        [ "expr_sum" ],
    ]),

    ( "expr_sum", [
        "expr_sum + expr_mult".split(),
        "expr_sum - expr_mult".split(),
        [ "expr_mult" ],
    ]),

    ( "expr_mult", [
        "expr_mult * operand".split(),
        [ "operand" ],
    ]),

    ( "operand", [
        [ "id" ],
        [ "literal" ],
        [ "call_statement" ],
        "( expr )".split(),
    ]),

    ( "call_statement", [
        "id ( )".split(),
        "id ( param_list )".split(),
    ]),

    ( "param_list", [
        "param_list , expr".split(),
        [ "expr" ],
    ]),

    # ( "if_statement", [
    #     "if ( expr ) statement".split(),
    #     "if ( expr ) statement else statement".split(),
    # ]),

    # ( "while_statement", [
    #     "while ( expr ) statement".split(),
    # ]),

    # ( "return_statement", [
    #     "return expr ;".split(),
    # ]),
]

# if you add something here, also check Token.bnf() function!
TERMINALS = [
    ( "keyword",  to_regex(words="return continue break def while if else".split()) ),
    # ( "builtin",  to_regex(words="return break".split()) ),
    ( "literal",  to_regex(chars=string.digits) ),
    ( "id",       to_regex(chars=string.ascii_letters + string.digits + "_") ),
    ( "operator", to_regex(words="+ - * = += -= *= < > == != ! && || <= >= << >> | & ^ <<< >>>".split()) ),
    ( "control",  to_regex(chars="{()};,", single=True) ),
]

WHITESPACE = to_regex(chars=string.whitespace)


class Position(object):
    def __init__(self, pos=-1, line=-1, col=-1):
        self.pos = pos
        self.line = line
        self.col = col

    def increase(self):
        self.pos += 1
        self.col += 1

    def new_line(self):
        self.pos += 1
        self.line += 1
        self.col = 0

    def clone(self):
        return Position(self.pos, self.line, self.col)


class Token(object):
    def __init__(self, lexeme, ttype="", position=None, tokens=[]):
        self.lexeme = lexeme
        self.type = ttype if ttype else lexeme
        self.tokens = tokens

        if not position and tokens:
            self.position = tokens[0].position
        else:
            self.position = position

    def print(self, depth = 0):
        logging.info(" " * depth + str(self))
        for i in self.tokens:
            i.print(depth + 1)

    def is_literal(self):
        return self.type == "literal"

    def is_id(self):
        return self.type == "id"

    def is_terminal(self):
        for i in TERMINALS:
            if self.type == i[0]:
                return True
        return False

    def is_expr(self):
        return self.type.startswith("expr")

    def _simplify_lists(self):
        if str(self).endswith("_list"):
            l = []
            for i in self.tokens:
                if str(i) == str(self):
                    i._simplify_lists()
                    l += i.tokens
                else:
                    l.append(i)
            self.tokens = l

    def _simplify(self):
        self._simplify_lists()

        for i in self.tokens:
            i._simplify()

        if str(self) == FINAL_STATE:
            return

        # strip control chars and keywords
        self.tokens = [ i for i in self.tokens if i.type not in ("control") ]

        # strip empty tokens
        self.tokens = [ i for i in self.tokens if i.is_terminal() or len(i.tokens) > 0 ]

        while len(self.tokens) == 1:
            if self.type.endswith("_list") or self.type.endswith("_statement"):
                break
            self._clone(self.tokens[0])

    def _clone(self, token):
        self.lexeme = token.lexeme
        self.type = token.type
        self.tokens = token.tokens
        self.position = token.position

    def bnf(self):
        # if self.type in ("operator", "control", "keyword", "builtin"):
        if self.is_literal() or self.is_id():
            return self.type
        return self.lexeme

    def line_info(self):
        return "In line {}, column {}: {}".format(
            self.position.line + 1, self.position.col + 1, str(self))

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
