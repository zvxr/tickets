
import tickets.config
import tornado.ioloop

from tickets.app.main import make_app


def run():
    app = make_app()
    app.listen(tickets.config.APP_PORT)
    tornado.ioloop.IOLoop.current().start()
