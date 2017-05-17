
import ticketer.app.handlers as handlers
import tornado.web


TICKET_REGEX = "[A-Z0-9]+"


def make_app():
    return tornado.web.Application(
        [
            (r"/ping", handlers.PingHandler),
            (r"/pong", handlers.PongHandler),
            (r"/ticket/({regex})".format(regex=TICKET_REGEX), handlers.TicketHandler),
            (r"/version", handlers.VersionHandler),
        ],
        default_handler_class=handlers.NotFoundHandler
    )
