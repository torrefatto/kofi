# -*- encoding: utf-8 -*-
"""This module holds the GraphQL implementation."""

from aiohttp import web


async def graphql(req: web.Request) -> web.Response:
    """Verify and handle the graphql request."""
    return web.json_response({"error": "not yet implemented"}, status_code=500)
