"""
Defines the Whoosh search engine.
"""

from collections import deque
from whoosh.analysis import StemmingAnalyzer, NgramWordAnalyzer, KeywordAnalyzer
from whoosh.fields import Schema, TEXT, KEYWORD
from whoosh.qparser import QueryParser, MultifieldParser, SequencePlugin
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
        analyzer = NgramWordAnalyzer(2, 4)

        try:
            ix = whoosh.index.open_dir(self.index)
            ix.close()
            create_index = False # index seems to be working fine
        except whoosh.index.EmptyIndexError:
            create_index = True

        if create_index:
            schema = Schema(
                name = TEXT(stored=True, analyzer=StemmingAnalyzer()),
                link = TEXT(stored=True),
                category = KEYWORD(stored=True, scorable=True, commas=True, analyzer=analyzer),
                description = TEXT(stored=True),
            )

            if not os.path.isdir(self.index):
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
            # TODO: Use the "csv" module for reading these files
            subdirs = deque()
            filename = self.path + ".csv"
            with open(filename) as file:
                for line_number, line in enumerate(file, 1):
                    if line.startswith("#"):
                        # Skip comments or header fields
                        continue

                    line = line.rstrip() # removes trailiing CRLF
                    fields = line.split(",")

                    try:
                        name = fields[2]
                        category = ",".join(fields[0].split(";"))
                        link = fields[1]
                    except IndexError as error:
                        print("%s:%d: %s: %r" % (os.path.basename(filename),
                            line_number, error, line))
                        raise RuntimeError("The CSV file seems to be invalid."
                                + " Check for proper use of separators.") from error

                    try:
                        # In the CSV file, it seems that the description is
                        # optional
                        description = fields[3]
                    except IndexError:
                        print("%s:%d: warning: missing description: %r" %
                                (os.path.basename(filename), line_number,
                                    line))
                        description = ""

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
        from natsort import natsorted
        out = dict()

        def sortOD(od):
            res = OrderedDict()
            for k, v in natsorted(od.items()):
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

    def select(self, query):
        qp = QueryParser("link", schema=self.ix.schema)

        results = []
        with self.ix.searcher() as s:
            for r in s.search(qp.parse(query), limit=10):
                return dict(r)

    def search(self, query, field="name", limit=200):
        qp = MultifieldParser(["name", "category", "description"], schema=self.ix.schema)

        with self.ix.searcher() as s:
            yield s.search(qp.parse(query), limit=limit)

    def suggest(self, query, field="name", limit=20):
        """Returns search suggestions for the given query."""
        out = []
        query = query.lower()
        curr = query.split(" ").pop()

        with self.ix.reader() as s:
            for i, hit in enumerate(s.expand_prefix("name", curr)):
                break
                out.append(str(hit, encoding="utf-8"))

            for i, hit in enumerate(s.expand_prefix("category", curr)):
                break
                out.append(str(hit, encoding="utf-8"))

        qp = MultifieldParser(["name", "category", "description"], schema=self.ix.schema)
        with self.ix.searcher() as s:
            for r in s.search(qp.parse(query), limit=limit):
                out.append(r["name"])

        return out
