#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import parser
import compiler
import logging
import argparse

def main():
    argparser = argparse.ArgumentParser(description="", epilog="")
    argparser.add_argument("-v", "--verbose", help="Show debug output", action="store_true")
    argparser.add_argument("file", help="A file to compile")
    args = argparser.parse_args()

    logging.basicConfig(level=(logging.DEBUG if args.verbose else logging.INFO),
                        format="%(levelname)s: %(message)s")

    p = parser.Parser()
    tree = p.parse_file(sys.argv[1])
    if not tree:
        return 1
    else:
        tree.print()

    out = compiler.compile(tree)
    logging.info("Assembler output:\n" + "\n".join(out))

    return 0


if __name__ == "__main__":
    sys.exit(main())
