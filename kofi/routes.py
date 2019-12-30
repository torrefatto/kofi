# -*- encoding: utf-8 -*-
"""The routes.

There is a REST API and a GraphQL API.

REST:

    - `/api/verify` [GET]
      query parameters:
      - 'cf': the Codice Fiscale string
      returns:
      - `{"isCorrect": boolean, "isOmocode": boolean, "cf": str}`
    - `/api/interpolate` [GET]
      query parameters:
      - `name`
      - `surname`
      - `gender`
      - `date_of_birth` in YYYYMMDD format
      - `place_of_birth`
      returns:
      cf- `{"cf": str}`

GraphQL:

    - `/graphql`
    accepts the following queries
    ```
    query verify(cf: String!) {
        isCorrect
        isOmocode
    }
    ```
    ```
    query interpolate(
        name: String!
        surname: String!
        gender: genderType!
        dateOfBirth: String!
        placeOfBirth: String!
    ) {
        codiceFiscale
    }
    ```
    being `genderType` an enum comprising `M` and `F` values

"""

from aiohttp import web
import typing as T

from kofi import rest
from kofi import graphql


def generate_app_routes(conf: T.Dict[T.Text, T.Any]) -> T.List[web.RouteDef]:
    """Generates the app routes using the configuration parameters."""
    app_routes = [
        web.get("/api/verify", rest.verify),
        web.get("/api/interpolate", rest.interpolate),
    ]
    if conf.get("graphiql"):
        app_routes.append(graphql.get_view(graphiql=True))
    else:
        app_routes.append(graphql.get_view(graphiql=False))
    return app_routes
