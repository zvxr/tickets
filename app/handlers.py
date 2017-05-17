
import ticketer
import ticketer.app.cache as cache
import time
import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.set_header('Content-Type', "application/json")

    def write_error(self, status_code, **kwargs):
        self.finish({
            'error': {
                'code': status_code,
                'message': self._reason,
            }
        })


class NotFoundHandler(BaseHandler):
    def get(self, *args, **kwargs):
        raise tornado.web.HTTPError(status_code=404, reason="Invalid resource path.")


class PingHandler(BaseHandler):
    def get(self):
        self.write({'message': "PONG"})


class PongHandler(BaseHandler):
    OK = "OK"
    ERROR = "ERROR"

    def _get_response(self, method, *args, **kwargs):
        """Executes method(*args, **kwargs) and returns dictionary with response information."""
        start_time = time.time()
        resp = {}
        try:
            method(*args, **kwargs)
            resp['message'] = self.OK
        except Exception as e:
            resp['message'] = self.ERROR
            resp['error'] = {'message': str(e)}
        finally:
            resp['response_time'] = int((time.time() - start_time) * 1000)

        return resp

    def get(self):
        resp = {'details': {}}
        resp['details']['redis'] = self._get_response(cache.ping)

        if all((s['message'] == self.OK for s in resp['details'].values())):
            resp['message'] = self.OK
        else:
            resp['message'] = self.ERROR
            self.set_status(500)

        self.write(resp)


class TicketHandler(BaseHandler):
    def get(self, ticket_id):
        # Example/Test 400 response.
        if ticket_id == "RESERVED":
            raise tornado.web.HTTPError(status_code=400, reason="Reserved Key.")

        self.write({'ticket_id': ticket_id})


class VersionHandler(BaseHandler):
    def get(self):
        self.write({'version': ticketer.__version__})
