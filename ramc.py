#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import parser
import logging
import argparse

# def main():
#     parser = argparse.ArgumentParser(description="", epilog="")
#     parser.add_argument("-v", "--verbose", help="Show debug output", action="store_true")
#     args = parser.parse_args()
#
#     if not args.profile and not args.api:
#         parser.error("an API and/or a profile has to specified.")
#         return 1
#
#     logging.basicConfig(level=(logging.DEBUG if args.verbose else logging.INFO),
#                         format="%(levelname)s:%(message)s")


def main():
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(message)s")

    if len(sys.argv) < 2:
        logging.error("No file specified")
        return 1

    p = parser.Parser()
    tree = p.parse_file(sys.argv[1])
    if not tree:
        return 1
    else:
        tree.print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
