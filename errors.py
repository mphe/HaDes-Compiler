# -*- coding: utf-8 -*-


class CompilerError(Exception):
    def __init__(self, msg):
        super(CompilerError, self).__init__(msg)

class CompilerSyntaxError(CompilerError):
    def __init__(self, msg):
        super(CompilerSyntaxError, self).__init__("Invalid syntax: " + msg)

class CompilerUndefinedError(CompilerError):
    def __init__(self, name):
        self.name = name
        super(CompilerUndefinedError, self).__init__("Use of undeclared identifier: " + name)

class CompilerUnsupportedError(CompilerError):
    def __init__(self, name):
        self.name = name
        super(CompilerUnsupportedError, self).__init__("Unsupported operation: " + name)

