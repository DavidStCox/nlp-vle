NLP-VLE
=======

This is a private project for David Cox.

First time installation
=======================

You need Python version 3+. To install the required packages, type

    $ pip3 install --user -r requirements.txt

The `--user` flag is optional.

Where to put text corpora
=========================

Create a new directory under `corpora` and put a new collection of documents
there.

Usage: search.py
================

To perform a search query, type

    $ ./search.py --query "horse"

It uses a default `--engine=whoosh`, document path `--docs=corpora/simple` and
index location `--index=indexes/simple`. Use `./search.py -h` to see more
options.

To provide search suggestions:

    $ ./search.py --suggest "horse"

Usage: server.py
================

    $ ./server.py --host=0.0.0.0 --port=8080 --engine=whoosh

How to push a new version to Heroku
===================================

  * Make sure that everything works straight out of the GitHub repo. I.e.
    `python3 search.py --port=8080` and try it in your browser.
  * Install the Heroku client on Linux if you haven't. For Linux:
    * `wget https://cli-assets.heroku.com/branches/stable/heroku-linux-amd64.tar.gz -O heroku.tar.gz`
    * `mkdir ~/bin`
    * `tar xzf herokut.ar.gz -C ~/bin`
    * `export PATH=${PATH}:~/bin/heroku/bin`
    * You need to do some login. Search for "Heroku CLI installation" to learn
      more about it. It's linked from here https://devcenter.heroku.com/articles/deploying-python
  * `git pull` to get the latest changes locally
  * `git clean -fdx` to clean out everything
  * `git push heroku master` to deploy a new version
  * Log on to Heroku. In right hand, upper corner, select "view logs" and see
    if there's an error (*after* you've tried the app on heroku).
  * We need to store files off of Heroku, because it restarts processes all the
    time. They have a free filestack addon we can probably use. This goes for
    the user data.
