#! /usr/bin/env python3

"""
Starts a webserver on your local machine.
"""

from flask import (
    Flask,
    render_template,
    make_response,
    request,
    session,
    redirect,
    url_for
)

import search # local
import argparse
import json
import os
import random
import sys
# replace with something more robust if necessary
import pickle

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

    p.add_argument("--corpus", type=str, default="ontology",
        help="Which corpus in the corpora/ subdirectory to use")

    p.add_argument("--engine", type=str, default="whoosh",
        help="Which search engine to use")

    p.add_argument("--list-engines", default=False, action="store_true",
        help="List available search engines")

    options = p.parse_args()

    if options.list_engines:
        print(" ".join(search.get_engines()))
        sys.exit(0)

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
    def __init__(self, *args, search_engine_name=None, corpus=None, **kw):
        super().__init__(*args, **kw)
        self._setup_routes()
        self.corpus = corpus
        self.corpus_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
            "corpora", self.corpus))

        self.index_path = os.path.realpath( os.path.join(
            os.path.dirname(__file__), "indexes", self.corpus))

        self.search_engine = search.get_engine(search_engine_name,
                path=self.corpus_path, index=self.index_path)

        self.secret_key = "asdfasdfasdfasd"

    def _setup_routes(self):
        route = lambda *args, **kw: self.add_url_rule(*args, **kw)
        route("/", view_func=self.index)
        route("/autocomplete", view_func=self.search_suggestions)
        route("/doc/<path:filename>", view_func=self.show_doc)
        route("/licenses", view_func=self.licenses)
        route("/logout", view_func=self.logout)
        route("/login", view_func=self.login, methods=["GET", "POST"])
        route("/results", view_func=self.results_view, methods=["GET", "POST"])
        route("/search/freetext", view_func=self.search, methods=["GET", "POST"])
        route("/search/navigation", view_func=self.navigation, methods=["GET", "POST"])
        route("/search/suggestions", view_func=self.search, methods=["GET", "POST"])

    def show_doc(self, filename):
        """Renders a document in the current corpus."""
        if "userid" not in session:
           return redirect(url_for('login'))
        doc = os.path.relpath(os.path.join(self.corpus_path, filename))

        # Prevent access of documents outside corpora folder
        if not os.path.realpath(doc).startswith(
                os.path.realpath(self.corpus_path)):
            raise RuntimeError("Can only view docs within corpus path: %s" %
                    doc)

        if doc.startswith(".."):
            return "Error: Trying to access file outside of corpus path"

        if not os.path.exists(doc):
            return "Error: File not found: %s" % filename

        with open(doc, "rt") as f:
            content = f.read()
            context = {
                "title": os.path.basename(doc),
                "content": content,
            }
            return make_response(render_template("doc.html", **context))

    def search_suggestions(self):
        """Returns search suggestions for the given query."""
        if "userid" not in session:
           return redirect(url_for('login'))

        query = request.args.get("query", "")

        result = {
            "query": query,
            "suggestions": self.search_engine.suggest(query),
        }

        return json.dumps(result)

    def results_view(self):
        """Performs the actual search."""
        if "userid" not in session:
           return redirect(url_for('login'))
        userid = session.get("userid")
        link = request.form.get("link", None)
        desired = request.form.get("desired", None)
        stats = request.form.get("stats", None)
        stats = json.loads(stats)

        data = self.get_data()
        tasks = data["tasks"]
        current_task = data["current_task"]

        time = stats[-1]["timestamp"] - stats[0]["timestamp"]
        task = tasks[current_task]
        task["stats"] = stats
        task["aborted"] = False
        task["finished"] = True
        data["current_task"] = current_task + 1

        self.set_data(data)

        context = {
            "title": "Task {} complete".format(int(current_task)+1),
            "index_view": url_for("index"),
            "link": link,
            "number_of_clicks": len(stats),
            "time_spent": time
        }

        return make_response(render_template("results.html", **context))

    def navigation(self):
        """Performs the actual search."""
        if "userid" not in session:
           return redirect(url_for('login'))
        userid = session.get("userid")
        data = self.get_data()
        tasks = data["tasks"]
        current_task = data["current_task"]

        context = {
            "title": "Search-navigation",
            "results_view": url_for("results_view"),
            "categories": {},
            "task": tasks[current_task],
        }

        context["categories"] = self.search_engine.category_tree()
        return make_response(render_template("navigation.html", **context))

    def search(self):
        """Performs the actual search."""
        if "userid" not in session:
           return redirect(url_for('login'))
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
                    url = "/doc/%s" % hit["link"]
                    title = hit["name"]
                    description = hit["description"]
                    category = hit["category"]
                    results.append((score, url, title, description, category))

            context["results"] = sorted(results, reverse=True)

        return make_response(render_template("search.html", **context))

    def index(self):
        """The test director page."""
        if "userid" not in session:
           return redirect(url_for('login'))
        userid = session.get("userid")
        tasks = self.get_data()["tasks"]

        context = {
                "title": "NLP-VLE",
                "userid": userid,
                "tasks": tasks,
                "logout_view": url_for("logout"),
                }

        response = make_response(render_template("index.html", **context))
        return response

    def login(self):
        """The site's landing page."""
        if request.method == 'POST':
            userid = request.form['userid']
            if len(userid) > 3:
                session['userid'] = userid
                self.initialize_test()
                return redirect(url_for('index'))

        return make_response(render_template("login.html", title="NLP-VLE"))


    def logout(self):
        """Logging out of the site."""
        session.pop("userid", None)
        return redirect(url_for('login'))

    # interrim persistence
    def get_data(self):
        userid = session.get("userid")
        filename = "user_data/data_{}.db".format(session.get("userid"))
        with open("user_data/data_{}.db".format(userid), "rb+") as f:
            return pickle.load(f)

    def set_data(self, data):
        userid = session.get("userid")
        filename = "user_data/data_{}.db".format(session.get("userid"))
        with open("user_data/data_{}.db".format(userid), "wb+") as f:
            pickle.dump(data, f)

    def initialize_test(self):
        filename = "user_data/data_{}.db".format(session.get("userid"))
        if os.path.exists(filename):
            return
        test_data = {}
        test_data['current_task'] = 0
        test_data['tasks'] = [
            {
                "name": "Task 1",
                "text": "Please, would you find Nobel price winner Adolf von Baeyer (ASAP)?", 
                "desired": "http://www.wikidata.org/entity/Q57078",
                "method": url_for("navigation"),
                "clicks": None,
                "aborted": None,
                "finished": False,
            },
            {"name": "Task 2", "text": "Find President Kennedy", "desired": "Q43911", "method": url_for("navigation"), "finished": False, },
            {"name": "Task 3", "text": "Find President Kennedy", "desired": "Q43912", "method": url_for("navigation"), "finished": False, },
            {"name": "Task 4", "text": "Find President Kennedy", "desired": "Q43913", "method": url_for("navigation"), "finished": False, },
            {"name": "Task 5", "text": "Find President Kennedy", "desired": "Q43914", "method": url_for("navigation"), "finished": False, },
            {"name": "Task 6", "text": "Find President Kennedy", "desired": "Q43915", "method": url_for("navigation"), "finished": False, },
        ]
        with open(filename, "wb+") as f:
            pickle.dump(test_data, f)

    def licenses(self):
        if "userid" not in session:
           return redirect(url_for('login'))

        context = {
            "title": "Licenses",
        }
        return make_response(render_template("licenses.html", **context))

def main():
    options = parse_arguments()

    app = SearchApp(__name__, search_engine_name=options.engine,
            corpus=options.corpus, template_folder=options.templates)
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
