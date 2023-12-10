#!/usr/bin/env python

from os import cpu_count, environ

from sanic import Sanic

from api import caching, routes

server = Sanic("TMovies", strict_slashes=False)

server.static("/", "web", index="index.html", strict_slashes=False)

routes.add_all(server)

server.register_middleware(caching.cache_request_middleware, "request")
server.register_middleware(caching.cache_response_middleware, "response")


if __name__ == "__main__":
    server.go_fast(
        host="0.0.0.0", port=int(environ.get("PORT", 5000)), workers=cpu_count() or 1
    )
