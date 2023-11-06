#!/usr/bin/env python

from os import cpu_count

from sanic import Sanic, redirect

from api import PORT, caching, routes

server = Sanic("TMovies", strict_slashes=False)

server.static("/web", "web", index="index.html", strict_slashes=False)
server.add_route(lambda _: redirect("/web/"), "/")

routes.add_all(server)

server.register_middleware(caching.cache_request_middleware, "request")
server.register_middleware(caching.cache_response_middleware, "response")


if __name__ == "__main__":
    server.go_fast(host="0.0.0.0", port=PORT, workers=cpu_count() or 1)
