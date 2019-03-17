# -*- coding: utf-8 -*-

from errors import *
import grammar
import logging

RA = "@ra"
SP = "@sp"
RV = "@rv"
PA = "@pa"
PB = "@pb"
LV = "@lv"

REGISTER_MAP = {
    SP: (7, "Stack pointer"),
    RA: (6, "Return adress"),
    RV: (5, "Return value"),
    LV: (4, "Temporary cache (lvalue)"),
    PA: (1, "A channel"),
    PB: (2, "B channel"),
}

# Stores asm output lines
ASM_LINES = []
ASM_INDENT = 0

LABEL_COUNTER = 0

# stores tuples with jump labels for break/continue commands (continue, break)
LOOP_STACK = []

def generate_labelname(name):
    global LABEL_COUNTER
    label = "label_{}_{}".format(str(LABEL_COUNTER), name)
    LABEL_COUNTER += 1
    return label

def generate_label(name, token=None):
    global ASM_INDENT
    indent, ASM_INDENT = ASM_INDENT, 0
    generate("\n{}:".format(name), token.line_info() if token else "")
    ASM_INDENT = indent

def generate(line, comment="", nonl=False):
    if comment:
        if not line:
            ASM_LINES.append("{}{}; {}".format("" if nonl else "\n", ASM_INDENT * "\t", comment))
        else:
            ASM_LINES.append("{}{}\t; {}".format(ASM_INDENT * "\t", line, comment))
    else:
        ASM_LINES.append(ASM_INDENT * "\t" + line)


class SymbolTable(object):
    # TODO: store info about which variables are already loaded to registers
    def __init__(self, token=None, varset=None, retlabel="", offset=0, args=[]):
        self._offset = offset
        self._returnlabel = retlabel
        self._symbols = []

        if token and not varset:
            varset = collect_vars(token)
        if varset:
            self._symbols = list(varset)

        if args:
            args = [ i.lexeme for i in args ]
            self._symbols = args + [ i for i in self._symbols if i not in args ]

    def get_return_label(self):
        return self._returnlabel

    def get_symbols(self):
        return self._symbols

    def lookup(self, name):
        """Returns the relative offset where the variable is stored"""
        localoffset = -len(self) - self._offset
        try:
            return localoffset + self._symbols.index(name)
        except ValueError:
            raise CompilerUndefinedError(name)

    def __len__(self):
        return len(self._symbols)


def collect_vars(token, varnames=None):
    """Retrieves all referenced variables in the given block as a set"""
    # "is not None" is correct, otherwise it will fail when the set is empty
    varnames = varnames if varnames is not None else set()
    for i in token.tokens:
        if i.type == "id" and token.type != "call_statement":
            varnames.add(i.lexeme)
        else:
            collect_vars(i, varnames)
    return varnames

def has_returns(token):
    """Returns true if the token contains any return statements"""
    for i in token.tokens:
        if i.lexeme == "return" or has_returns(i):
            return True
    return False

def literal_to_int(token, logical=False):
    return int(int(token.lexeme) != 0 if logical else token.lexeme)


def compile(tokentree):
    if not str(tokentree) == grammar.FINAL_STATE:
        raise CompilerError("Not a valid program: " + str(tokentree))

    for k,v in REGISTER_MAP.items():
        generate("@def {} r{}".format(k[1:], str(v[0])), v[1])

    for token in tokentree.tokens:
        if token.type == "function":
            compile_function(token.tokens[1:])
        elif token.type == "statement":
            raise CompilerUnsupportedError("Statements outside functions not supported yet")

    global ASM_LINES
    out = ASM_LINES
    ASM_LINES = []
    return out


def compile_function(tokens):
    global ASM_INDENT

    name = tokens[0]
    statements = tokens[1] if len(tokens) == 2 else tokens[2]
    args = [] if len(tokens) == 2 else tokens[1].tokens

    for i in args:
        if not i.is_id():
            raise CompilerSyntaxError(name.lexeme + ": function argument is not an identifier")

    returnlabel = generate_labelname("return") if has_returns(statements) else ""
    saveregisters = [ RA, LV, PA, PB ]
    symtable = SymbolTable(statements,
                           retlabel=returnlabel,
                           offset=len(saveregisters),
                           args=args)
    framesize = len(symtable) + len(args) + len(saveregisters)

    # stack structure: param1, param2, ..., registers, ..., local1, local2, ..., return adress

    generate("", "Local variables/parameters:")
    for i in symtable.get_symbols():
        generate("", "{}:\t{}".format(i, str(symtable.lookup(i))), True)

    generate("@code {} {{".format(name.lexeme.upper()))
    ASM_INDENT += 1
    generate("", "Prepare stack")
    generate("ADDI  @sp, @sp, #" + str(framesize), "Increment stack pointer")
    # generate("STORE @ra, @sp, #-1", "Save return address")

    generate("", "Backup registers")
    for k,v in enumerate(saveregisters, 1):
        generate("STORE {}, @sp, #-{}".format(v, k))

    # function code
    compile_block(statements.tokens, symtable, RV)

    if returnlabel:
        generate_label(returnlabel)

    generate("", "Restore registers")
    for k,v in enumerate(saveregisters, 1):
        generate("LOAD {}, @sp, #-{}".format(v, k))

    # generate("LOAD @ra, @sp, #-1", "Restore return adress")
    generate("SUBI @sp, @sp, #" + str(framesize), "Restore stack pointer")
    generate("JREG @ra", "Return to address in @ra")
    ASM_INDENT -= 1
    generate("@}\n")

def compile_block(tokens, symtable, dest=RV, loop=False):
    for i in tokens:
        generate("", i.line_info())

        if i.type != "keyword" and (i.is_terminal() or i.is_expr() or i.type == "call_statement"):
            compile_evaluate(i, symtable, dest)
        elif i.lexeme == "break":
            if loop:
                generate("JMP #" + LOOP_STACK[-1][1], "Break loop")
        elif i.lexeme == "continue":
            if loop:
                generate("JMP #" + LOOP_STACK[-1][0], "Continue loop")
        else:
            compile_statement(i.tokens, symtable, dest, loop)

def compile_statement(tokens, symtable, dest=RV, loop=False):
    global LOOP_STACK

    name = tokens[0].lexeme

    if name == "if":
        compile_if(tokens[1:3] + tokens[4:], symtable, dest, loop)
    elif name == "while":
        compile_while(tokens[1:], symtable, dest)
    elif name == "return":
        compile_return(tokens[1:], symtable, dest)
    else:
        raise CompilerUnsupportedError(name)

def compile_if(tokens, symtable, dest=RV, loop=False):
    cond = tokens[0]
    truecode = tokens[1]
    falsecode = tokens[2] if len(tokens) > 2 else None

    afterlabel = generate_labelname("endif")
    jumplabel = generate_labelname("else") if falsecode else afterlabel

    # evaluate condition
    compile_evaluate(cond, symtable, dest)
    generate("BEQZ {} #{}".format(dest, jumplabel), "Check condition")
    compile_block(truecode.tokens if truecode.type == "statement_list" else [ truecode ],
                  symtable, dest, loop)

    if falsecode:
        generate("JMP #" + afterlabel)
        generate_label(jumplabel, falsecode)
        compile_block(falsecode.tokens if falsecode.type == "statement_list" else [ falsecode ],
                      symtable, dest, loop)

    generate_label(afterlabel)

def compile_while(tokens, symtable, dest=RV):
    global LOOP_STACK

    cond = tokens[0]
    code = tokens[1]
    endless = False

    if cond.is_literal():
        if literal_to_int(cond, True) == 0:
            return
        else:
            endless = True

    startlabel = generate_labelname("while")
    afterlabel = generate_labelname("endwhile")
    LOOP_STACK.append((startlabel, afterlabel))

    generate_label(startlabel)
    if not endless:
        compile_evaluate(cond, symtable, dest)
        generate("BEQZ {} #{}".format(dest, startlabel), "Check condition")
    compile_block(code.tokens if code.type == "statement_list" else [ code ],
                  symtable, dest, True)
    generate("JMP #" + startlabel, "Restart loop")
    generate_label(afterlabel)

    LOOP_STACK.pop()

def compile_return(tokens, symtable, dest=RV):
    if len(tokens) > 0:
        compile_evaluate(tokens[0], symtable, dest)
    else:
        generate("LDI {} #0".format(dest))
    generate("JMP #" + symtable.get_return_label(), "return")

def compile_call(tokens, symtable, dest=RV):
    name = tokens[0].lexeme.upper()
    args = tokens[1].tokens if len(tokens) > 1 else []

    if name in ("PREAD", "PWRITE"):
        if len(args) != 2:
            raise CompilerError("pread/pwrite requires exactly 2 arguments")

        if not args[1].is_literal():
            raise CompilerError("pread/pwrite adress must be a literal")

        op = "IN" if name == "PREAD" else "OUT"
        compile_evaluate(args[0], symtable, dest)
        generate("{} {}, #{}".format(op, dest, str(literal_to_int(args[1]))))
        return

    generate("", "Pushing function parameters on the stack")
    generate("ADDI  @sp, @sp, #" + str(len(args)), "Increment stack pointer")
    for k,v in enumerate(args):
        compile_evaluate(v, symtable, dest)
        generate("STORE {}, @sp, #-{}".format(dest, len(args) - k))

    generate("JAL {}, #{}".format(RA, name), "Call " + name)
    if dest != RV:
        generate("ADDI {} {} #0".format(dest, RV), "Move return value to " + dest)


def compile_evaluate(token, symtable, dest=RV, logical=False):
    # TODO: consider merging this into compile_expr
    if token.is_literal():
        val = str(literal_to_int(token, logical))
        generate("LDI {}, #{}".format(dest, val))
        return
    elif token.is_id():
        compile_varfetch(token, symtable, dest)
        if logical:
            generate("SNEI {}, {}, #0".format(dest, dest), "Convert to bool")
    elif token.type == "call_statement":
        compile_call(token.tokens, symtable, dest)
    elif token.is_expr():
        compile_expr(token, symtable, dest, logical)
    else:
        raise CompilerUnsupportedError(str(token))


def compile_varfetch(token, symtable, register=RV):
    if token.is_id():
        offset = symtable.lookup(token.lexeme)
        generate("LOAD {} {}, #{}".format(register, SP, str(offset)),
                 "load {} into register {}".format(token.lexeme, register))
    else:
        raise CompilerError("Not a variable: " + str(token))

def compile_expr(token, symtable, dest=RV, logical=False):
    if token.type == "expr_assignment":
        compile_assignment(token.tokens, symtable, dest)
    else:
        compile_expr_alu(token.tokens, symtable, dest, logical)

def compile_expr_alu(tokens, symtable, dest=RV, logical=False):
    OP_MAP = {
        "+": "ADD",
        "-": "SUB",
        "*": "MUL",
        "|": "OR",
        "&": "AND",
        "^": "XOR",
        "<<": "SHL",
        ">>": "SHR",
        "<<<": "CSHL",
        ">>>": "CSHR",
        "&&": "AND",
        "||": "OR",
        "<": "SLT",
        ">": "SGT",
        "<=": "SLE",
        ">=": "SGE",
        "==": "SEQ",
        "!=": "SNE",
    }

    a = tokens[0]
    op = str(tokens[1])
    b = tokens[2]

    try:
        cmd = OP_MAP[op]
    except KeyError:
        raise CompilerUnsupportedError(op)

    immed = a.is_literal() ^ b.is_literal()
    logical = True if logical else op == "&&" or op == "||"

    # make sure the literal is always the second parameter
    if immed and a.is_literal():
        a, b = b, a

    if immed:
        compile_evaluate(a, symtable, dest, logical)
        generate("{}I {}, #{}".format(cmd, dest, str(literal_to_int(b, logical))))
    else:
        # let's hope this works
        # make sure not to store anything in @rv, in case of a function call
        if a.is_expr() and b.is_expr():
            compile_evaluate(a, symtable, LV, logical)
            compile_evaluate(b, symtable, PB, logical)
            generate("{} {}, {}, {}".format(cmd, dest, LV, PB))
        else:
            compile_evaluate(a, symtable, PA, logical)
            compile_evaluate(b, symtable, PB, logical)
            generate("{} {}, {}, {}".format(cmd, dest, PA, PB))

    if logical and op not in ("<", ">", "<=", ">=", "==", "!="):
        generate("SNEI {}, {}, #0".format(dest, dest), "Convert to bool")

def compile_assignment(tokens, symtable, dest=RV):
    d = tokens[0]
    op = str(tokens[1])
    val = tokens[2]

    compile_evaluate(val, symtable, dest)

    offset = symtable.lookup(d.lexeme)
    generate("STORE {} {}, #{}".format(dest, SP, str(offset)),
             "save result ({}) to {}".format(dest, d.lexeme))
