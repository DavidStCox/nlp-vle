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

from user_data import (
        get_user_data,
        save_user_data,
        get_all_users)

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
        route("/test_results_dump", view_func=self.test_results_dump_view, methods=["GET", "POST"])
        route("/logout", view_func=self.logout)
        route("/login", view_func=self.login, methods=["GET", "POST"])
        route("/search/finalizer", view_func=self.finalizer_view, methods=["GET", "POST"])
        route("/search/results", view_func=self.results_view, methods=["GET", "POST"])
        route("/search/freetext", view_func=self.search, methods=["GET", "POST"])
        route("/search/navigation", view_func=self.navigation, methods=["GET", "POST"])
        route("/search/suggestions", view_func=self.search_suggest, methods=["GET", "POST"])

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

    def finalizer_view(self):
        """Performs the actual search."""
        if "userid" not in session:
           return redirect(url_for('login'))

        userid = session.get("userid")
        user = get_user_data(userid)
        user.end_task()
        save_user_data(user)

        return redirect(url_for('index'))
        
    def test_results_dump_view(self):
        """Dump all the test data to a csv file."""
        if "userid" not in session:
           return redirect(url_for('login'))

        # template template template
        def format_header():
            line = []
            line.append("userid")
            line.append("index")
            line.append("task id")
            line.append("task text")
            line.append("clicks")
            line.append("time")
            line.append("success")
            line.append("completed")
            return ";\t".join(line)

        def format_line(user, task, index):
            line = []
            line.append(user.userid)
            line.append(str(index))
            line.append(task.get_id())
            line.append(task.text)
            line.append(task.number_of_clicks())
            line.append(task.time_elapsed())
            line.append(task.success())
            line.append(task.is_finished())
            return ";\t".join(line)

        output = []
        output.append(format_header())
        users = get_all_users()
        for user in users:
            for index, task in enumerate(user.get_tasks()):
                output.append(format_line(user, task, index))

        return make_response("<br>".join(output))

    def results_view(self):
        """Performs the actual search."""
        if "userid" not in session:
           return redirect(url_for('login'))

        link = request.form.get("link", None)
        stats = json.loads(request.form.get("stats", "[]"))

        userid = session.get("userid")
        user = get_user_data(userid)
        task = user.get_task()
        task.link_found = link
        task.append_stats(stats)
        save_user_data(user)
        record = self.search_engine.select(link)

        context = {
            "finalizer_view": url_for("finalizer_view"),
            "test_view": url_for(task.view),
            "record": record,
            "task": task,
        }

        return make_response(render_template("results.html", **context))

    def navigation(self):
        """Performs the actual search."""
        if "userid" not in session:
           return redirect(url_for('login'))
        userid = session.get("userid")
        user = get_user_data(userid)
        task = user.get_task()

        context = {
            "title": "Search-navigation",
            "results_view": url_for("results_view"),
            "categories": {},
            "task": task,
        }

        context["categories"] = self.search_engine.category_tree()
        return make_response(render_template("navigation.html", **context))

    def search_suggest(self):
        """Performs the actual search."""
        if "userid" not in session:
           return redirect(url_for('login'))

        stats = json.loads(request.form.get("stats", "[]"))
        query = request.form.get("query", None)
        perform_search = query is not None

        userid = session.get("userid")
        user = get_user_data(userid)
        task = user.get_task()
        task.append_stats(stats)
        save_user_data(user)

        context = {
            "title": "Search",
            "query": query,
            "results_view": url_for("results_view"),
            "autocomplete": True,
            "task": task
        }

        if perform_search:
            self.logger.info("Search: %s" % repr(query))

            results = []
            for hits in self.search_engine.search(query):
                for hit in hits:
                    score = hit.score
                    url = "%s" % hit["link"]
                    title = hit["name"]
                    description = hit["description"]
                    category = hit["category"]
                    results.append((score, url, title, description, category))

            context["results"] = sorted(results, reverse=True)

        return make_response(render_template("search.html", **context))

    def search(self):
        """Performs the actual search."""
        if "userid" not in session:
           return redirect(url_for('login'))
        query = request.form.get("query", None)
        stats = json.loads(request.form.get("stats", "[]"))
        perform_search = query is not None

        userid = session.get("userid")
        user = get_user_data(userid)
        task = user.get_task()
        task.append_stats(stats)
        save_user_data(user)

        context = {
            "title": "Search",
            "query": query,
            "results_view": url_for("results_view"),
            "autocomplete": False,
            "task": task
        }

        if perform_search:
            self.logger.info("Search: %s" % repr(query))

            results = []
            for hits in self.search_engine.search(query):
                for hit in hits:
                    score = hit.score
                    url = "%s" % hit["link"]
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
        user = get_user_data(userid)
        tasks = user.get_tasks()

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
                user = get_user_data(userid)
                save_user_data(user)
                return redirect(url_for('index'))

        return make_response(render_template("login.html", title="NLP-VLE"))


    def logout(self):
        """Logging out of the site."""
        session.pop("userid", None)
        return redirect(url_for('login'))


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
