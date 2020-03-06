====
KoFi
====

Microservice to check or create a Codice Fiscale

* Free software: GPLv3
* For documentation either run ``make docs`` in a properly configured environment (see Develop_),
  or go to https://torrefatto.github.io/kofi
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

Alternatively, you can use the development docker image. Build it with:

  .. code-block:: shell

    $ make docker-dev-build

Run it with:

  .. code-block:: shell

    $ make docker-dev-run

You'll find the server on ``localhost:1312``. You will find a graphiql_ page (needs internet
connectivity :-/ ).

Production
----------

Build the package, install and run it:

  .. code-block:: shell

    $ make dist

Otherwise, build the docker image:

  .. code-block:: shell

    $ make docker-build

This will build ``torrefatto/kofi:<tag>`` with the tag being the current version.
You can run it and bind to the ``1312`` port:

  .. code-block:: shell

    $ docker run -t torrefatto/kofi:<tag>

or in whatever orchestrator you prefer.

API
===

ReST
----

There are two endpoints:

* ``/api/verify`` [GET]
query parameters:
  - ``cf``: the Codice Fiscale string

returns:

  .. code-block:: json

    {"isCorrect": "<bool>", "isOmocode": "<bool>", "cf": "<str>"}

* ``/api/interpolate`` [GET]
query parameters:
  - ``name``
  - ``surname``
  - ``gender``
  - ``date_of_birth`` in YYYYMMDD format
  - ``place_of_birth``

returns:

  .. code-block:: json

    {"cf": "<str>"}


GraphQL
-------

As usual, there is just the ``/graphql`` endpoint. It accepts the following queries:

 .. code-block:: graphql

    schema {
      query: codiceFiscaleQuery
    }

    type codiceFiscaleQuery {
      """The body of the verify response."""
      verify(
        """The Codice Fiscale string."""
        cf: String!
      ): verifyType

      """Query to obtain one person's codice fiscale"""
      interpolate(
        """Person's first name(s)"""
        name: String!

        """Person's last name(s)"""
        surname: String!

        """Person's official gender"""
        gender: Gender!

        """Person's date of birth"""
        dateOfBirth: String!

        """Person's place of birth"""
        placeOfBirth: String!
      ): interpolateType
    }

    """One's official gender."""
    enum Gender {
      """Male"""
      M

      """Female"""
      F
    }

    """The result of person's data interpolation"""
    type interpolateType {
      """One person's codice fiscale."""
      codiceFiscale: String
    }

    """The result of checks on the CF."""
    type verifyType {
      """If the CF is omocode, ."""
      isOmocode: Boolean

      """If the CF is correct."""
      isCorrect: Boolean
    }

being ``genderType`` an enum comprising ``M`` and ``F`` values

.. _pipenv: https://pipenv.kennethreitz.org/en/latest/
.. _GNU_make: https://www.gnu.org/software/make/
.. _graphiql: 


