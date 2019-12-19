# -*- encoding: utf-8 -*-
"""The views that handle the REST API are defined here."""

from aiohttp import web

from codicefiscale import codicefiscale


async def verify(req: web.Request) -> web.Response:
    """Validate and handle verify request."""
    cf = req.query.get("cf")
    req.app["log"].info(f"Received request for {cf}")
    if not cf:
        return web.json_response({"error": "malformed request", "cf": cf}, status=400)
    if codicefiscale.is_valid(cf):
        return web.json_response({"result": True, "cf": cf})
    else:
        return web.json_response({"result": False, "cf": cf})


async def interpolate(req: web.Request) -> web.Response:
    """Validate and handle interpolate request."""
    name = req.query.get("name")
    surname = req.query.get("surname")
    gender = req.query.get("gender")
    date_of_birth = req.query.get("date_of_birth")
    place_of_birth = req.query.get("place_of_birth")
    req.app["log"].info(
        f"Received request for ({name}, {surname}, {gender}, {date_of_birth}, {place_of_birth})"
    )
    try:
        cf = codicefiscale.encode(surname, name, gender, date_of_birth, place_of_birth)
    except ValueError as e:
        return web.json_response(
            {"error": "malformed request", "error_msg": str(e)}, status=400,
        )
    return web.json_response({"result": cf})
