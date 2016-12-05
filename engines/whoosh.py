"""
Defines the Whoosh search engine.
"""

from collections import deque
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT, KEYWORD
from whoosh.qparser import QueryParser
import contextlib
import os
import whoosh

class WhooshSearchEngine():
    def __init__(self, path, index):
        """Initializes the search engine.

        Args:
            path: Path to document root to index
            index: Path to where the index will be placed.
        """
        self.path = path
        self.index = index

        if not os.path.isdir(self.index):
            schema = Schema(
                title = TEXT(stored=True),
                filename = TEXT(stored=True),
                body = TEXT(analyzer=StemmingAnalyzer()),
                suggestions = TEXT(),
                suggestion_phrases = KEYWORD(commas=True, lowercase=True)
            )

            os.mkdir(self.index)

            print("Creating index %s" % os.path.relpath(self.index))
            with contextlib.closing(whoosh.index.create_in(self.index,
                schema)) as ix:
                self._index(ix, self.path)

        print("Opening index %s" % self.index)
        self.ix = whoosh.index.open_dir(self.index)

    def _index(self, ix, root):
        def index_directory(writer, path, depth_first=False):
            """A recursive indexer."""
            subdirs = deque()

            for item in sorted(os.listdir(path)):
                filename = os.path.join(path, item)

                if os.path.isdir(filename):
                    if depth_first:
                        index_directory(writer, filename)
                    else:
                        subdirs.append(filename)
                    continue

                #try:
                with open(filename, "rt") as file:
                    body = file.read()
                #except Exception as e:
                    #print(str(e))

                print("Indexing %s" % os.path.relpath(filename))
                writer.add_document(
                    title=os.path.basename(filename),
                    filename=os.path.relpath(filename, self.path),
                    body=body,
                    suggestions=body,
                    suggestion_phrases=body)

            for subdir in subdirs:
                index_directory(writer, subdir, depth_first=depth_first)

        writer = ix.writer()
        index_directory(writer, root)
        writer.commit()

    def search(self, query, field="body", limit=20):
        qp = QueryParser(field, schema=self.ix.schema)
        p = qp.parse(query)

        with self.ix.searcher() as s:
            yield s.search(p, limit=limit)

        #return self.searcher.search(p, limit=limit)
