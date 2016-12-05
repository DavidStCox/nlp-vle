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

To index documents in `corpora/simple` and put the index in `indexes/simple`:

    $ ./search.py --engine=whoosh --docs=corpora/simple \
        --index=indexes/simple

You can always to `git clean -fdx` to clean out all index files. To perform a
search query:

    $ ./search.py --query "horse"

By default, it will use Whoosh, `corpora/simple` and `indexes/simple`.

Usage: server.py
================

    $ ./server.py --host=0.0.0.0 --port=8080 --engine=whoosh

