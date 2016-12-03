#! /usr/bin/env python3

"""
Creates search indices and performs search.
"""

import argparse
import os
import sys
import whoosh

def main():
    p = argparse.ArgumentParser()

    p.add_argument("--path", type=str, default=None,
        help="Path to the directory containing text corpora")

    p.add_argument("--corpus", type=str, default="simple",
        help="Subdirectory to use as a text corpus")

    options = p.parse_args()

    if options.path is None:
        options.path = os.path.realpath(
                os.path.join(os.path.dirname(__file__), "corpora"))

    if not os.path.isdir(options.path):
        raise FileNotFoundError(options.path)

    options.corpus = os.path.realpath(os.path.join(options.path,
        options.corpus))

    if not os.path.isdir(options.corpus):
        raise FileNotFoundError(options.corpus)

    return options

if __name__ == "__main__":
    if sys.version_info[0] <= 2:
        print("You need Python 3+ to run this program.")
        sys.exit(1)
    try:
        main()
        sys.exit(0)
    except FileNotFoundError as e:
        print("Could not find file or directory: %s" % e)
    except KeyboardInterrupt:
        pass
    sys.exit(1)
