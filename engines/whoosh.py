"""
Defines the Whoosh search engine.
"""

from collections import deque
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT, KEYWORD
from whoosh.qparser import QueryParser, MultifieldParser
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
                name = TEXT(stored=True),
                link = TEXT(stored=True),
                category = KEYWORD(stored=True, scorable=True, commas=True),
                description = TEXT(stored=True),
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
            with open(self.path + ".csv") as file:
                for line in file:
                    if line.startswith("#"):
                        continue

                    fields = line.split(",")

                    category = ",".join(fields[0].split(";"))
                    link = fields[1]
                    name = fields[2]
                    description = fields[3]

                    writer.add_document(
                        name=name,
                        link=link,
                        category=category,
                        description=description)

        writer = ix.writer()
        index_directory(writer, root)
        writer.commit()


    def category_tree(self):
        from collections import OrderedDict
        out = dict()

        def sortOD(od):
            res = OrderedDict()
            for k, v in sorted(od.items()):
                if isinstance(v, dict):
                    res[k] = sortOD(v)
                else:
                    res[k] = v
            return res

        with self.ix.reader() as s:
            for r in s.all_stored_fields():
                categories = r["category"].split(",")

                current = out
                for cat in categories:
                    if cat not in current:
                        current[cat] = {}
                    current = current[cat]

                current[r["name"]] = r["link"]

        return sortOD(out)

    def search(self, query, field="name", limit=200):
        qp = MultifieldParser(["name", "category", "description"], schema=self.ix.schema)

        with self.ix.searcher() as s:
            yield s.search(qp.parse(query), limit=limit)

    def suggest(self, query, field="name", limit=20):
        """Returns search suggestions for the given query."""
        out = []
        with self.ix.reader() as s:
            for hit in s.expand_prefix("name", query):
                out.append(str(hit, encoding="utf-8"))
            for hit in s.expand_prefix("category", query):
                out.append(str(hit, encoding="utf-8"))

        qp = QueryParser("name", schema=self.ix.schema)
        with self.ix.searcher() as s:
            for r in s.search(qp.parse(query), limit=limit):
                out.append(r["name"])

        qp = QueryParser("category", schema=self.ix.schema)
        with self.ix.searcher() as s:
            for r in s.search(qp.parse(query), limit=limit):
                out.append(r["category"])
        return out
