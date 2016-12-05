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

