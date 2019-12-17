# -*- encoding: utf-8 -*-
"""The views that handle the REST API are defined here."""

from aiohttp import web

from codicefiscale import codicefiscale


async def verify(req: web.Request) -> web.Response:
    """Validate and handle verify request."""
    cf = req.query.get("cf")
    req.app["log"].info(f"Received request for cf -> {cf}")
    if not cf:
        return web.json_response({"error": "malformed request", "cf": cf}, status=400)
    if codicefiscale.is_valid(cf):
        return web.json_response({"result": True, "cf": cf})
    else:
        return web.json_response({"result": False, "cf": cf})


async def interpolate(req: web.Request) -> web.Response:
    """Validate and handle interpolate request."""
    pass
