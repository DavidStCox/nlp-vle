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
import argparse
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

    options = p.parse_args()

    if options.templates is None:
        options.templates = os.path.realpath(
                os.path.join(os.path.dirname(__file__), "templates"))

    if not os.path.isdir(options.templates):
        raise FileNotFoundError(options.templates)

    return options

class SearchApp(Flask):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._setup_routes()

    def _setup_routes(self):
        self.add_url_rule("/", view_func=self.index)

        self.add_url_rule("/search/freetext", view_func=self.search,
                methods=["GET", "POST"])

        self.add_url_rule("/search/suggestions", view_func=self.search,
                methods=["GET", "POST"])

        self.add_url_rule("/search/navigation", view_func=self.search,
                methods=["GET", "POST"])

    def get_suggestions(self):
        """Returns (real time) queries back to the user."""

        results = [
            "suggestion 1",
            "suggestion 2",
            "suggestion 3",
        ]

        return json.dumps(results)

    def search(self):
        """Performs the actual search."""
        query = request.form.get("query", None)

        if query is not None:
            self.logger.info("Search: %s" % repr(query))

            # Score, URL, Title, Excerpt
            results = (
                (random.uniform(0,1), "?first-hit", "RandomSite1", "blah blah"),
                (random.uniform(0,1), "?second-hit", "RandomSite2", "blah blah"),
                (random.uniform(0,1), "?third-hit", "RandomSite2", "blah blah"),
            )
        else:
            results = []

        context = {
            "title": "Search",
            "results": sorted(results, reverse=True),
            "query": query,
        }
        return render_template("search.html", **context)

    def index(self):
        """The site's landing page."""
        return render_template("index.html", title="NLP-VLE")

def main():
    options = parse_arguments()

    app = SearchApp(__name__, template_folder=options.templates)
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