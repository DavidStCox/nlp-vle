#! /usr/bin/env python3

"""
Creates search indexes and performs search.
"""

import argparse
import contextlib
import shutil
import sys
import tempfile

def get_engines():
    """Returns a dictionary of available search engines."""
    # Import engines here to make normal program startup faster
    from engines import WhooshSearchEngine
    return {
        "whoosh": WhooshSearchEngine,
    }

def get_engine(name, path, index):
    """Initializes and returns named search engine.

    Args:
        path: Path to root of documents to index
        index: Path to the directory containing the index.
    """
    engines = get_engines()
    Engine = engines[name]
    return Engine(path=path, index=index)

def parse_args():
    """Parses the command line arguments."""
    p = argparse.ArgumentParser()

    p.add_argument("--docs", type=str, default="corpora/ontology",
        help="Path to root directory of documents to index.")

    p.add_argument("--index", type=str, default="indexes/ontology",
        help="Index directory.")

    p.add_argument("--engine", "-e", type=str, default="whoosh",
        help="Search engine to use, one of: %s" % " ".join(get_engines()))

    p.add_argument("--list-engines", "-l", default=False, action="store_true",
        help="List available search engines.")

    p.add_argument("--query", "-q", type=str, default=None,
        help="Performs a search on the given query.")

    p.add_argument("--suggest", "-s", metavar="QUERY", default=None,
        help="Print search suggestions for given query.")

    opts = p.parse_args()

    if opts.list_engines:
        print(" ".join(get_engines()))
        sys.exit(0)

    return opts

def main():
    opts = parse_args()

    try:
        engine = get_engine(opts.engine, opts.docs, opts.index)
    except KeyError as e:
        print("Unknown engine: %s" % e)
        sys.exit(1)

    if opts.query is not None:
        for results in engine.search(opts.query):
            print(results)
            for result in results:
                print(result)

    if opts.suggest is not None:
        for phrase in engine.suggest(opts.suggest):
            print(phrase)

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
