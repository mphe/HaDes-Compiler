#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import parser


def main():
    if len(sys.argv) < 2:
        print("No file specified")
        return 1

    p = parser.Scanner()
    p.parse_file(sys.argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
