====
KoFi
====

Microservice to check or create a Codice Fiscale

* Free software: GPLv3
* For documentation, run ``make docs`` in a properly configured environment (see Develop_).
* Dumb as it should be


How to
======

Develop
-------

To prepare a development environment use pipenv_. Install it and then run

  .. code-block:: shell

    $ pipenv install --dev .

To enter a development-ready environment

  .. code-block:: shell

    $ pipenv shell

You'll get a shell with all the needed dependencies. If you have GNU_make_ installed, a set
of targets are available to ease the tasks. In the following, these targets will be used.
You can avoid using them, reading the `Makefile` source and using the commands therein instead.

To start a development session

  .. code-block:: shell

    $ pipenv run kofi

Production
----------

Build the package and run it:

  .. code-block:: shell

    $ make dist

Otherwise, build the docker image:

  .. code-block:: shell

    $ make docker-image


.. _pipenv: https://pipenv.kennethreitz.org/en/latest/
.. _GNU_make: https://www.gnu.org/software/make/
