#! /usr/bin/env python3

"""
Creates search indexes and performs search.
"""

from collections import deque
from engine_whoosh import WhooshSearchEngine
import argparse
import contextlib
import os
import shutil
import sys
import tempfile
import whoosh
import whoosh.index

# Each engine must specify (class, init-args, init-keywords)
ENGINES = {
    "whoosh": WhooshSearchEngine,
}

def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument("--path", type=str, default=None,
        help="Path to the directory containing text corpora")

    p.add_argument("--corpus", type=str, default="simple",
        help="Subdirectory to use as a text corpus")

    p.add_argument("--index-path", type=str, default=None,
        help="Directory to hold search indexes.")

    p.add_argument("--engine", type=str, default="whoosh",
        help="Search engine to use")

    p.add_argument("--query", "-q", type=str, default=None,
        help="If specified, perform a search query.")

    p.add_argument("--suggestions", default=False, action="store_true",
        help="If specified alongside --query, show query suggestions")

    options = p.parse_args()

    if options.path is None:
        options.path = os.path.realpath(
                os.path.join(os.path.dirname(__file__), "corpora"))

    if not os.path.isdir(options.path):
        raise FileNotFoundError(options.path)

    if not os.path.isdir(os.path.join(options.path, options.corpus)):
        raise FileNotFoundError(options.corpus)

    if options.index_path is None:
        options.index_path = os.path.realpath(
                os.path.join(os.path.dirname(__file__), "indexes"))
    return options

def main():
    opts = parse_args()

    if opts.engine not in ENGINES:
        print("Unknown engine %s. Only know of %s" % (repr(opts.engine),
            sorted(opts.engine.keys())))
        sys.exit(1)

    # Get engine class and initialize it
    Engine = ENGINES[opts.engine]
    s = Engine(doc_path=os.path.join(opts.path, opts.corpus),
            index_path=os.path.join(opts.index_path, opts.corpus))

    if opts.query is not None:
        for results in s.search(opts.query):
            print(results)
            for result in results:
                print(result)

    if opts.suggestions:
        for suggestion in s.suggest(opts.query):
            print(suggestion)

@contextlib.contextmanager
def tempdir():
    directory = tempfile.mkdtemp()
    try:
        yield directory
    finally:
        shutil.rmtree(directory)

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
