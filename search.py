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

class SearchEngine():
    def __init__(self, index_path):
        self.schema = Schema(
            title=TEXT(stored=True),
            body=TEXT(analyzer=StemmingAnalyzer()))

        self.index_path = index_path
        self.ix = whoosh.index.create_in(self.index_path, self.schema)

    def index(self, root):
        writer = self.ix.writer()

        for filename in os.listdir(root):
            print("Indexing %s" % filename)
            filename = os.path.join(root, filename)
            try:
                with open(filename, "rt") as file:
                    writer.add_document(
                        title=os.path.basename(filename),
                        body=file.read(),
                    )
            except Exception as e:
                print(str(e))

        writer.commit()

    def search(self, query, field="body"):
        qp = QueryParser(field, schema=self.ix.schema)
        p = qp.parse(query)

        with self.ix.searcher() as s:
            yield s.search(p)

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
    with tempdir() as index_location:
        s = SearchEngine(index_location)
        s.index(opts.corpus)

        query = "bird"
        print("Performing example search for %s:" % repr(query))
        for no, result in enumerate(s.search(query)):
            print(result)
        print("%d results" % (1+no))

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
