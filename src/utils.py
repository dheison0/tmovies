import dataclasses
import json
from typing import Tuple

from aiohttp import ClientSession


class HTTPBadStatusCode(Exception):
    def __init__(self, code: int):
        super().__init__(f"website returned http code {code}")


async def http_get(url: str, params: dict = {}) -> Tuple[int, str]:
    session = ClientSession()
    try:
        response = await session.get(url, params=params, timeout=30)
        text = await response.text()
    finally:
        await session.close()
    return response.status, text


def clear_title(title: str) -> str:
    to_remove = ["torrent", "web-dl", "download"]
    new_title = title.strip().lower()
    for remove in to_remove:
        new_title = new_title.split(remove)[0]
    new_title = new_title.strip().title()
    return new_title


def dataclass2bytes(data) -> bytes:
    data_dict = dataclasses.asdict(data)
    data = json.dumps(data_dict)
    return data.encode()
