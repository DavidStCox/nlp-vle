#! /usr/bin/env python3

"""
Creates search indices and performs search.
"""

from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.qparser import QueryParser
import argparse
import contextlib
import os
import shutil
import sys
import tempfile
import whoosh
import whoosh.index

def parse_args():
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

def main():
    opts = parse_args()
    with tempdir() as indexdir:
        #print("Tempdir: %s" % indexdir)
        ix = index(opts, indexdir)

        query = "bird"
        print("Performing example search for %s:" % repr(query))
        results = list(search(ix, field="body", query="bird"))
        for result in results:
            print(result)
        print("%d results" % len(results))

def search(ix, field, query):
    qp = QueryParser(field, schema=ix.schema)
    p = qp.parse(query)

    with ix.searcher() as s:
        yield s.search(p)

def index(opts, indexdir):
    schema = Schema(
                title=TEXT(stored=True),
                body=TEXT(analyzer=StemmingAnalyzer()))

    print("Indexing %s" % os.path.relpath(opts.corpus))

    ix = whoosh.index.create_in(indexdir, schema)
    writer = ix.writer()

    for filename in os.listdir(opts.corpus):
        print("Indexing %s" % filename)
        filename = os.path.join(opts.corpus, filename)
        with open(filename, "rt") as file:
            writer.add_document(
                title=os.path.basename(filename),
                body=file.read(),
            )

    print("Committing")
    writer.commit()
    return ix

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
