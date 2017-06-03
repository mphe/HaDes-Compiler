#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import parser


def main():
    if len(sys.argv) < 2:
        print("No file specified")
        return 1

    p = parser.Parser()
    tree = p.parse_file(sys.argv[1])
    print_token(tree, 0)

    return 0


def print_token(token, depth):
    if token:
        print(" " * depth + str(token))
        for i in token.tokens:
            print_token(i, depth + 1)


if __name__ == "__main__":
    sys.exit(main())
