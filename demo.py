
import ticketer.config
import tornado.ioloop

from ticketer.app.main import make_app


def run():
    app = make_app()
    app.listen(ticketer.config.APP_PORT)
    tornado.ioloop.IOLoop.current().start()
