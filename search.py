#! /usr/bin/env python3

"""
Creates search indexes and performs search.
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
    def __init__(self, doc_path, index_path):
        self.doc_path = doc_path
        self.index_path = index_path


        if not os.path.isdir(self.index_path):
            schema = Schema(
                title=TEXT(stored=True),
                body=TEXT(analyzer=StemmingAnalyzer()))

            os.mkdir(self.index_path)

            with contextlib.closing(whoosh.index.create_in(self.index_path,
                schema)) as ix:
                SearchEngine._index(ix, self.doc_path)

        self.ix = whoosh.index.open_dir(self.index_path)

    @staticmethod
    def _index(ix, root):
        writer = ix.writer()

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

    def search(self, query, field="body", limit=20):
        qp = QueryParser(field, schema=self.ix.schema)
        p = qp.parse(query)

        with self.ix.searcher() as s:
            yield s.search(p, limit=limit)

        #return self.searcher.search(p, limit=limit)

def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument("--path", type=str, default=None,
        help="Path to the directory containing text corpora")

    p.add_argument("--corpus", type=str, default="simple",
        help="Subdirectory to use as a text corpus")

    p.add_argument("--index-path", type=str, default=None,
        help="Directory to hold search indexes.")

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

    s = SearchEngine(doc_path=os.path.join(opts.path, opts.corpus),
                     index_path=os.path.join(opts.index_path, opts.corpus))

    query = "bird"
    print("Performing example search for %s:" % repr(query))
    for results in s.search(query):
        print(results)
        for result in results:
            print(result)

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
