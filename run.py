from os import cpu_count

from sanic import Sanic

from api import PORT, routes

server = Sanic(__name__)
routes.add_all(server)

if __name__ == '__main__':
    server.go_fast(host='0.0.0.0', port=PORT, workers=cpu_count() or 1)
