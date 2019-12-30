# -*- encoding: utf-8 -*-
"""Test the routes defined in kofi.routes"""

from asyncio import AbstractEventLoop, get_running_loop
from contextlib import closing
from json import JSONDecoder
import socket
import typing as T
from unittest import mock

from aiohttp import web
import pytest
import pytest_aiohttp

from kofi.config import DEFAULT_LOG_CONF
from kofi.main import setup as setup_app


# From: https://stackoverflow.com/a/45690594
def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


CONF = {
    "host": "127.0.0.1",
    "port": find_free_port(),
    "log": DEFAULT_LOG_CONF,
    "graphiql": True,
}


def get_app(loop: AbstractEventLoop) -> web.Application:
    return setup_app(CONF, loop)


def get_app_no_graphiql(loop: AbstractEventLoop) -> web.Application:
    conf = CONF.copy()
    conf["graphiql"] = False
    return setup_app(conf, loop)


@pytest.mark.parametrize(
    "cf,is_correct,is_omocode",
    [
        ["RSSMRA99E05H501A", True, False],
        ["RSSMRA99E05H50GP", True, True],
        ["BCDFGH12A55Z123F", False, False],
    ],
)
async def test_rest_verify(
    loop: AbstractEventLoop,
    aiohttp_client: pytest_aiohttp.TestClient,
    cf: T.Text,
    is_correct: bool,
    is_omocode: bool,
) -> None:
    """Test the /api/verify REST endpoint."""
    app = get_app(loop)
    client = await aiohttp_client(app)
    resp_blob = await client.get(f"/api/verify?cf={cf}")
    resp_json = await resp_blob.text()
    resp = JSONDecoder().decode(resp_json)
    assert resp.get("cf") == cf
    assert resp.get("isCorrect") == is_correct
    assert resp.get("isOmocode") == is_omocode


async def test_rest_interpolate(
    loop: AbstractEventLoop, aiohttp_client: pytest_aiohttp.TestClient
) -> None:
    """Test the /api/interpolate REST endpoint."""
    app = get_app(loop)
    client = await aiohttp_client(app)
    resp_blob = await client.get(
        f"/api/interpolate?name=Mario&surname=Rossi&gender=M&date_of_birth=1999-05-05&place_of_birth=Roma"
    )
    resp_json = await resp_blob.text()
    resp = JSONDecoder().decode(resp_json)
    assert resp["cf"] == "RSSMRA99E05H501A"


@pytest.mark.parametrize(
    "query_string",
    [
        "surname=Rossi&gender=M&date_of_birth=1999-05-05&place_of_birth=Roma",
        "name=Mario&gender=M&date_of_birth=1999-05-05&place_of_birth=Roma",
        "name=Mario&surname=Rossi&date_of_birth=1999-05-05&place_of_birth=Roma",
        "name=Mario&surname=Rossi&gender=M&place_of_birth=Roma",
        "name=Mario&surname=Rossi&gender=M&date_of_birth=1999-05-05",
    ],
)
async def test_rest_interpolate_err(
    loop: AbstractEventLoop,
    aiohttp_client: pytest_aiohttp.TestClient,
    query_string: T.Text,
) -> None:
    """Test the /api/interpolate REST endpoint with wrong input."""
    app = get_app(loop)
    client = await aiohttp_client(app)
    resp_blob = await client.get(f"/api/interpolate?{query_string}")
    resp_json = await resp_blob.text()
    resp = JSONDecoder().decode(resp_json)
    assert resp["error"] == "malformed request"
    assert "error_msg" in resp


@pytest.mark.parametrize(
    "cf,is_correct,is_omocode",
    [
        ["RSSMRA99E05H501A", True, False],
        ["RSSMRA99E05H50GP", True, True],
        ["BCDFGH12A55Z123F", False, False],
    ],
)
async def test_graphql_verify(
    loop: AbstractEventLoop,
    aiohttp_client: pytest_aiohttp.TestClient,
    cf: T.Text,
    is_correct: bool,
    is_omocode: bool,
) -> None:
    """Test the /graphql endpoint."""
    app = get_app(loop)
    client = await aiohttp_client(app)
    resp_blob = await client.post(
        "/graphql",
        data=f"""
        query {{
            verify(cf: "{cf}"){{
                isCorrect
                isOmocode
            }}
        }}
        """,
        headers={"Content-Type": "application/graphql"},
    )
    resp_json = await resp_blob.text()
    resp = JSONDecoder().decode(resp_json)
    assert resp["data"]["verify"]["isCorrect"] == is_correct
    assert resp["data"]["verify"]["isOmocode"] == is_omocode


async def test_graphql_interpolate(
    loop: AbstractEventLoop, aiohttp_client: pytest_aiohttp.TestClient,
) -> None:
    """Test the /graphql endpoint."""
    app = get_app(loop)
    client = await aiohttp_client(app)
    resp_blob = await client.post(
        "/graphql",
        data="""
        query {
            interpolate(
                name: "Mario",
                surname: "Rossi",
                gender: M,
                dateOfBirth: "1999-05-05",
                placeOfBirth: "Roma"
            ){
                codiceFiscale
            }
        }
        """,
        headers={"Content-Type": "application/graphql"},
    )
    resp_json = await resp_blob.text()
    resp = JSONDecoder().decode(resp_json)
    assert resp["data"]["interpolate"]["codiceFiscale"] == "RSSMRA99E05H501A"


async def test_graphiql(
    loop: AbstractEventLoop, aiohttp_client: pytest_aiohttp.TestClient,
) -> None:
    """Test the graphiql frontend."""
    app = get_app(loop)
    client = await aiohttp_client(app)
    resp = await client.get("/graphql")
    assert resp.status == 200
    cont = await resp.text()
    assert "graphiql" in cont


async def test_no_graphiql(
    loop: AbstractEventLoop, aiohttp_client: pytest_aiohttp.TestClient,
) -> None:
    """Test the graphiql frontend absence."""
    app = get_app_no_graphiql(loop)
    client = await aiohttp_client(app)
    resp_blob = await client.get("/graphql")
    assert resp_blob.status == 400
    resp_json = await resp_blob.text()
    resp = JSONDecoder().decode(resp_json)
    assert resp["errors"][0]["message"] == "Must provide query string."
