# -*- encoding: utf-8 -*-
"""Test the graphql module."""

from collections import OrderedDict, namedtuple
import typing as T

from graphql import graphql
import pytest

from kofi.graphql import schema

VERIFY_QUERY = """
query {{
    verify(cf: "{}"){{
        isCorrect,
        isOmocode
    }}
}}
"""

INTERPOLATE_QUERY = """
query {{
    interpolate(
        name: "{name}",
        surname: "{surname}",
        gender: {gender},
        dateOfBirth: "{date_of_birth}",
        placeOfBirth: "{place_of_birth}"
    ){{
        codiceFiscale
    }}
}}
"""

PersonalData = namedtuple(
    "PersonalData", ["name", "surname", "gender", "place", "date"]
)


def verify_result(is_correct: bool, is_omocode: bool) -> OrderedDict:
    return OrderedDict(
        [
            (
                "verify",
                OrderedDict([("isCorrect", is_correct), ("isOmocode", is_omocode)]),
            )
        ]
    )


def interpolate_result(cf: T.Text) -> OrderedDict:
    return OrderedDict([("interpolate", OrderedDict([("codiceFiscale", cf)]))])


@pytest.mark.parametrize(
    "cf, expected",
    [
        ["RSSMRA99E05H501A", verify_result(True, False)],
        ["RSSMRA99E05H50GP", verify_result(True, True)],
        ["BCDFGH12A55Z123F", verify_result(False, False)],
    ],
)
def test_verify(cf: T.Text, expected: T.List[T.Any]) -> None:
    """Test the verify query."""
    result = graphql(schema, VERIFY_QUERY.format(cf))
    assert result.data == expected


@pytest.mark.parametrize(
    "personal_data, expected",
    [
        [
            PersonalData("Mario", "Rossi", "M", "Roma", "1999-05-05",),
            interpolate_result("RSSMRA99E05H501A"),
        ],
        [
            PersonalData("Maria", "Bianchi", "F", "Milano", "1970-12-27"),
            interpolate_result("BNCMRA70T67F205L"),
        ],
    ],
)
def test_interpolate(personal_data: namedtuple, expected: T.Text) -> None:
    """Test the interpolate query."""
    result = graphql(
        schema,
        INTERPOLATE_QUERY.format(
            name=personal_data.name,
            surname=personal_data.surname,
            gender=personal_data.gender,
            date_of_birth=personal_data.date,
            place_of_birth=personal_data.place,
        ),
    )
    assert result.data == expected
