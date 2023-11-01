from os import cpu_count

from sanic import Sanic, redirect

from api import PORT, routes

server = Sanic(__name__, strict_slashes=False)
server.add_route(lambda _: redirect("/web/"), "/")
server.static("/web", "web", index="index.html", strict_slashes=False)
routes.add_all(server)

if __name__ == "__main__":
    server.go_fast(host="0.0.0.0", port=PORT, workers=cpu_count() or 1)
