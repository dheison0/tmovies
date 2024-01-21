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


def clear_title(title: str) -> str:
    from_items = ["torrent", "web-dl", "download"]
    new_title = title.strip().lower()
    for item in from_items:
        new_title = new_title.split(item)[0]
    new_title = new_title.strip().title()
    return new_title
