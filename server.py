#! /usr/bin/env python3

"""
Starts a webserver on your local machine.
"""

from flask import (
    Flask,
    render_template,
    request,
)

from flask.views import View
from search import SearchEngine # local module
import argparse
import json
import os
import random
import sys

def parse_arguments():
    """Fetches and verifies command line arguments."""
    p = argparse.ArgumentParser()

    p.add_argument("--host", type=str, default="0.0.0.0",
        help="Host/IP-address to bind the server to.")

    p.add_argument("--port", type=int, default=8080,
        help="Port to bind the server to.")

    p.add_argument("--templates", type=str, default=None,
        help="Path to the Jinja2 templates directory")

    p.add_argument("--static", type=str, default=None,
        help="Path to the /static files diretory")

    p.add_argument("--corpus", type=str, default="simple",
        help="Which corpus in the corpora/ subdirectory to use")

    options = p.parse_args()

    if options.templates is None:
        options.templates = os.path.realpath(
                os.path.join(os.path.dirname(__file__), "templates"))

    if options.static is None:
        options.static = os.path.realpath(
                os.path.join(os.path.dirname(__file__), "static"))

    if not os.path.isdir(options.templates):
        raise FileNotFoundError(options.templates)

    if not os.path.isdir(options.static):
        raise FileNotFoundError(options.static)

    return options

class SearchApp(Flask):
    def __init__(self, *args, corpus=None, **kw):
        super().__init__(*args, **kw)
        self._setup_routes()
        self.corpus = corpus
        self.corpus_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
            "corpora", self.corpus))

        self.index_path = os.path.realpath( os.path.join(
            os.path.dirname(__file__), "indexes", self.corpus))

        self.search_engine = SearchEngine(doc_path=self.corpus_path,
                index_path=self.index_path)

    def _setup_routes(self):
        route = lambda *args, **kw: self.add_url_rule(*args, **kw)
        route("/", view_func=self.index)
        route("/autocomplete", view_func=self.search_suggestions)
        route("/doc/<path:filename>", view_func=self.show_doc)
        route("/licenses", view_func=self.licenses)
        route("/search/freetext", view_func=self.search, methods=["GET", "POST"])
        route("/search/navigation", view_func=self.search, methods=["GET", "POST"])
        route("/search/suggestions", view_func=self.search, methods=["GET", "POST"])

    def show_doc(self, filename):
        """Renders a document in the current corpus."""
        doc = os.path.relpath(os.path.join(self.corpus_path, filename))
        if doc.startswith(".."):
            return "Error: Trying to access file outside of corpus path"

        if not os.path.exists(doc):
            return "Error: File not found: %s" % filename

        with open(doc, "rt") as f:
            content = f.read()
            context = {
                "title": "Document: %s" % os.path.basename(doc),
                "content": content,
            }
            return render_template("doc.html", **context)

    def search_suggestions(self):
        """Returns search suggestions for the given query."""

        query = request.args.get("query", "")

        result = {
            "query": query,
            "suggestions": [
                "suggestion 1",
                "suggestion 2",
                "suggestion 3 - %d" % random.randint(1,100),
            ],
        }

        return json.dumps(result)

    def search(self):
        """Performs the actual search."""
        query = request.form.get("query", None)
        perform_search = query is not None

        context = {
            "title": "Search",
            "query": query,
            "autocomplete": True,
        }

        if perform_search:
            self.logger.info("Search: %s" % repr(query))

            results = []
            for hits in self.search_engine.search(query):
                for hit in hits:
                    score = hit.score
                    url = "/doc/%s" % os.path.basename(hit["filename"])
                    title = hit["title"]
                    excerpt = "..."
                    results.append((score, url, title, excerpt))

            context["results"] = sorted(results, reverse=True)

        return render_template("search.html", **context)

    def index(self):
        """The site's landing page."""
        return render_template("index.html", title="NLP-VLE")

    def licenses(self):
        context = {
            "title": "Licenses",
        }
        return render_template("licenses.html", **context)

def main():
    options = parse_arguments()

    app = SearchApp(__name__, corpus=options.corpus,
            template_folder=options.templates)
    app.run(host=options.host, port=options.port)

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
