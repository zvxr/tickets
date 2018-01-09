import app.handlers as handlers
import app.config as config
import tornado.web

from app.ticket_gen import TICKET_REGEX


class Application(tornado.web.Application):
    """Tornado 4.5 breaks sphinx. Provide workaround for autotornado."""
    @property
    def handlers(self):
        handlers = []

        def process_router(router: tornado.web.ReversibleRuleRouter):
            for rule in router.rules:
                if isinstance(rule.target, tornado.web.ReversibleRuleRouter):
                    process_router(rule.target)
                elif (
                    isinstance(rule.target, type) and 
                    issubclass(rule.target, tornado.web.RequestHandler)
                ):
                    if isinstance(rule.matcher, tornado.routing.PathMatches):
                        spec = type(
                            'spec',
                            (),
                            dict(handler_class=rule.target,
                            regex=rule.matcher.regex)
                        )
                        handlers.append(spec)

        process_router(self.default_router)

        return [[None, handlers]]


app = Application(
    [
        (r"/ping", handlers.PingHandler),
        (r"/pong", handlers.PongHandler),
        (r"/ticket", handlers.TicketHandler),
        (r"/ticket/(%s)" % TICKET_REGEX, handlers.TicketIdHandler),
        (r"/version", handlers.VersionHandler),
    ],
    default_handler_class=handlers.NotFoundHandler
)


def run():
    global app
    app.listen(config.APP_PORT)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    run()
