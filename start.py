#!/usr/bin/env python

from os import cpu_count, environ

from sanic import Sanic

from src.api.routes import bp as api_routes

server = Sanic("TMovies")
server.blueprint(api_routes)


if __name__ == "__main__":
    server.go_fast(
        host="0.0.0.0", port=int(environ.get("PORT", 5000)), workers=cpu_count() or 1
    )
