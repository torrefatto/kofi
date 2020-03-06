Welcome to KoFi's documentation!
======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   readme
   installation
   usage
   modules


Overview
========

``KoFi`` is a simple (dumb) server that exposes a simple API to work
with the italian state ID number (called `codice fiscale`).
It is just a wrapper around the python-codicefiscale_ library.

It exposes a ReST and a GraphQL API that absolve the same task.
You can either:

* verify that a known `codice fiscale` is valid (and eventually
  `omocode`, that is a deduplicated code with respect to the default algorithm
  to avoid collision with the one of another person).

* obtain the base version of the `codice fiscale`, given the needed
  input data


.. _python-codicefiscale: https://github.com/fabiocaccamo/python-codicefiscale/
