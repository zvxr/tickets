
import tickets
import tickets.app.cache as cache
import tickets.app.ticket_gen as ticket_gen
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


class BaseTicketHandler(BaseHandler):
    DEFAULT_EXPIRATION = 60000  # 60 seconds.

    @property
    def client(self):
        if not hasattr(self, '_client') or self._client is None:
            self._client = cache.get_client()
        return self._client

    def _delete_ticket(self, ticket_id):
        """
        Expire a ticket by ID.
        This will silently succeed if ticket ID did not exist.
        """
        self.client.expire(ticket_id)

    def _generate_ticket(self, ticket_id, expiration, payload):
        """Set ticket in cache."""
        # TODO: detect and handle conflicts.
        self.client.setex(ticket_id, expiration, payload)

    def _get_ticket(self, ticket_id):
        """Return payload from cache."""
        return self.client.get(ticket_id)


class NotFoundHandler(BaseHandler):
    def get(self, *args, **kwargs):
        raise tornado.web.HTTPError(
            status_code=404,
            reason="Invalid resource path."
        )


class PingHandler(BaseHandler):
    def get(self):
        self.write({'message': "PONG"})


class PongHandler(BaseHandler):
    OK = "OK"
    ERROR = "ERROR"

    def _get_response(self, method, *args, **kwargs):
        """
        Executes method(*args, **kwargs) and returns dictionary with response
        information.
        """
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


class TicketHandler(BaseTicketHandler):
    def post(self):
        # TODO: support payload and expiration params.
        ticket_id = ticket_gen.get()
        self._generate_ticket(ticket_id, self.DEFAULT_EXPIRATION, 1)
        self.write({'ticket_id': ticket_id})


class TicketIdHandler(BaseTicketHandler):
    def delete(self, ticket_id):
        self._delete_ticket(ticket_id)
        self.write({'message': "success"})

    def get(self, ticket_id):
        # Example/Test 400 response.
        if ticket_id == "RESERVED":
            raise tornado.web.HTTPError(
                status_code=400,
                reason="Reserved Key."
        )

        payload = self._get_ticket(ticket_id)
        self.write({'payload': payload, 'ticket_id': ticket_id})


class VersionHandler(BaseHandler):
    def get(self):
        self.write({'version': tickets.__version__})
