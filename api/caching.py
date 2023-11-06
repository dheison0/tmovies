from dataclasses import dataclass, field
from time import time

from sanic.request import Request
from sanic.response import HTTPResponse

DEFAULT_TIME = 300
ERROR_TIME = 60


@dataclass
class CacheData:
    response: HTTPResponse
    created_at: float = field(default_factory=time)

    def is_expired(self):
        life_time = DEFAULT_TIME if self.response.status < 400 else ERROR_TIME
        return (time() - self.created_at) >= life_time


data: dict[str, CacheData] = {}


async def cache_request_middleware(request: Request) -> HTTPResponse | None:
    if cache := data[request.raw_url]:
        if not cache.is_expired():
            return cache.response
        data.pop(request.raw_url)


async def cache_response_middleware(request, response) -> HTTPResponse:
    if request.raw_url not in data:
        data[request.raw_url] = CacheData(response)
