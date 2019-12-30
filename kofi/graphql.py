# -*- encoding: utf-8 -*-
"""This module holds the GraphQL implementation."""

import typing as T

from aiohttp import web
from aiohttp_graphql import GraphQLView
from codicefiscale import codicefiscale
from graphql import (
    GraphQLArgument,
    GraphQLNonNull,
    GraphQLString,
    GraphQLBoolean,
    GraphQLField,
    GraphQLSchema,
    GraphQLEnumValue,
    GraphQLObjectType,
    GraphQLEnumType,
)
from graphql.execution.base import ResolveInfo


def is_correct(root: T.Any, info: T.Any, **args: T.Dict[T.Text, T.Any]) -> bool:
    cf = args.get("cf")
    if cf:
        try:
            return codicefiscale.is_valid(cf)
        except ValueError:
            return False
    raise ValueError("Missing argument.")


def is_omocode(root: T.Any, info: T.Any, **args: T.Dict[T.Text, T.Any]) -> bool:
    cf = args.get("cf")
    if cf:
        try:
            return codicefiscale.is_omocode(cf)
        except ValueError:
            return False
    raise ValueError("Missing argument.")


def resolve_verify(root: T.Any, info: T.Any, **args: T.Any) -> T.Dict[T.Text, bool]:
    return {
        "isOmocode": is_omocode(root, info, **args),
        "isCorrect": is_correct(root, info, **args),
    }


def resolve_interpolate(
    root: T.Any, info: ResolveInfo, **args: T.Any
) -> T.Dict[T.Text, T.Text]:
    name = args.get("name")
    surname = args.get("surname")
    gender = args.get("gender")
    place_of_birth = args.get("placeOfBirth")
    date_of_birth = args.get("dateOfBirth")
    if all(
        [
            arg is not None
            for arg in (name, surname, gender, place_of_birth, date_of_birth)
        ]
    ):
        return {
            "codiceFiscale": codicefiscale.encode(
                surname, name, gender, date_of_birth, place_of_birth
            )
        }
    raise ValueError("Missing argument.")


codiceFiscaleArg = GraphQLArgument(
    type=GraphQLNonNull(GraphQLString), description="The Codice Fiscale string."
)

verifyType = GraphQLObjectType(
    "verifyType",
    description="The result of checks on the CF.",
    fields=lambda: {
        "isOmocode": GraphQLField(
            GraphQLBoolean, description="If the CF is omocode, ."
        ),
        "isCorrect": GraphQLField(GraphQLBoolean, description="If the CF is correct."),
    },
)

nameArg = GraphQLArgument(
    type=GraphQLNonNull(GraphQLString), description="Person's first name(s)"
)

surnameArg = GraphQLArgument(
    type=GraphQLNonNull(GraphQLString), description="Person's last name(s)"
)

genderType = GraphQLEnumType(
    "Gender",
    description="One's official gender.",
    values={
        "M": GraphQLEnumValue("M", description="Male"),
        "F": GraphQLEnumValue("F", description="Female"),
    },
)

genderArg = GraphQLArgument(
    type=GraphQLNonNull(genderType), description="Person's official gender"
)

placeOfBirthArg = GraphQLArgument(
    type=GraphQLNonNull(GraphQLString), description="Person's place of birth"
)

dateOfBirthArg = GraphQLArgument(
    type=GraphQLNonNull(GraphQLString), description="Person's date of birth"
)

interpolateType = GraphQLObjectType(
    "interpolateType",
    description="The result of person's data interpolation",
    fields=lambda: {
        "codiceFiscale": GraphQLField(
            GraphQLString, description="One person's codice fiscale."
        )
    },
)

codiceFiscaleQuery = GraphQLObjectType(
    "codiceFiscaleQuery",
    fields=lambda: {
        "verify": GraphQLField(
            verifyType,
            description="The body of the verify response.",
            args={"cf": codiceFiscaleArg},
            resolver=resolve_verify,
        ),
        "interpolate": GraphQLField(
            interpolateType,
            description="Query to obtain one person's codice fiscale",
            args={
                "name": nameArg,
                "surname": surnameArg,
                "gender": genderArg,
                "dateOfBirth": dateOfBirthArg,
                "placeOfBirth": placeOfBirthArg,
            },
            resolver=resolve_interpolate,
        ),
    },
)

schema = GraphQLSchema(query=codiceFiscaleQuery, types=[verifyType, interpolateType])


def get_view(graphiql: bool) -> web.View:
    """Get the graphql aiohttp view."""
    return web.view("/graphql", GraphQLView(schema=schema, graphiql=graphiql))
