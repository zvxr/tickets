
import tickets.app.handlers as handlers
import tornado.web

from tickets.app.ticket_gen import TICKET_REGEX


def make_app():
    return tornado.web.Application(
        [
            (r"/ping", handlers.PingHandler),
            (r"/pong", handlers.PongHandler),
            (r"/ticket", handlers.TicketHandler),
            (r"/ticket/({regex})".format(regex=TICKET_REGEX), handlers.TicketIdHandler),
            (r"/version", handlers.VersionHandler),
        ],
        default_handler_class=handlers.NotFoundHandler
    )
