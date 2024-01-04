from http import HTTPStatus
from typing import List, Tuple

from aiohttp import ClientSession
from sanic.request import Request
from sanic.response import json


class HTTPBadStatusCode(Exception):
    def __init__(self, code: int):
        super().__init__(f"website returned http code {code}")


async def http_get(url: str, params: dict = {}) -> Tuple[int, str]:
    session = ClientSession()
    response = await session.get(url, params=params, timeout=30)
    text = await response.text()
    await session.close()
    return response.status, text


def check_queries(handler, queries: List[str]):
    async def checker(request: Request, *args, **kwargs):
        for query in queries:
            if request.args.get(query) is None:
                return json(
                    body={"error": f'url argument "{query}" not defined'},
                    status=HTTPStatus.BAD_REQUEST,
                )
        response = await handler(request, *args, **kwargs)
        return response

    return checker
