# -*- encoding: utf-8 -*-
"""The routes.

There is a REST API and a GraphQL API.

REST:

    - `/api/verify` [GET]
      query parameters:
      - 'cf': the Codice Fiscale string
    - `/api/interpolate` [GET]
      query parameters:
      - `name`
      - `surname`
      - `gender`
      - `date_of_birth` in YYYYMMDD format
      - `place_of_birth`

GraphQL:

    - `/graphql`
    accepts the following queries
    ```
    query verify(cf: $cf) {
        isCorrect
    }
    ```
    ```
    query interpolate(
        name: $name
        surname: $surname
        gender: $gender
        dateOfBirth: $dateOfBirth
        placeOfBirth: $placeOfBirth
    ) {
        codiceFiscale
    }
    ```

"""

from aiohttp import web
import typing as T

from kofi import rest
from kofi import graphql

app_routes: T.List[web.RouteDef] = [
    web.get("/api/verify", rest.verify),
    web.get("/api/interpolate", rest.interpolate),
    web.post("/graphql", graphql.graphql),
]
