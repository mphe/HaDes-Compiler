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
    argparser.add_argument("-o", "--output", nargs=1, metavar="file", help="Write output to a file")
    argparser.add_argument("file", help="A file to compile")
    args = argparser.parse_args()

    logging.basicConfig(level=(logging.DEBUG if args.verbose else logging.INFO),
                        format="%(levelname)s: %(message)s")

    p = parser.Parser()
    tree = p.parse_file(args.file)
    if not tree:
        return 1
    else:
        tree.print()

    out = compiler.compile(tree)
    logging.info("Assembler output:\n" + "\n".join(out))

    if args.output:
        with open(args.output[0], "w") as f:
            f.write("\n".join(out))

    return 0


if __name__ == "__main__":
    sys.exit(main())
