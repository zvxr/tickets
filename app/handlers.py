
import tickets
import tickets.app.cache as cache
import tickets.app.ticket_gen as ticket_gen
import time
import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    def get_int_value(self, arg_name, default=None):
        value = self.get_argument(arg_name, default=default)
        if value:
            return int(value)
        return value

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

    def _generate_ticket(self, ticket_id, ttl, payload):
        """Set ticket in cache."""
        # TODO: detect and handle conflicts.
        self.client.setex(ticket_id, payload, ttl)

    def _get_ticket(self, ticket_id, expire):
        """
        Return payload from cache.
        If expire is True, set to None atomically.
        """
        # TODO: best practices for atomically fetch/expire-- not just null.
        if expire:
            return self.client.getset(ticket_id, None)
        else:
            return self.client.get(ticket_id)

    def _update_ticket(self, ticket_id, payload=None, ttl=None):
        """Set ticket payload and/or TTL in cache."""
        if payload:
            self.client.set(ticket_id, payload)

        if ttl:
            self.client.expire(ticket_id, ttl)


class NotFoundHandler(BaseHandler):
    def get(self, *args, **kwargs):
        raise tornado.web.HTTPError(
            status_code=404,
            reason="Invalid resource path."
        )


class PingHandler(BaseHandler):
    """
    .. http:get:: /ping

       Route for basic health monitoring.

       **Example request**:

       .. sourcecode:: http

          GET /ping HTTP/1.1

       **Example response**:

       .. sourcecode:: http

          HTTP/1.1 200 OK
          Vary: Accept
          Content-Type: text/javascript

          {
              "message": "PONG"
          }

        :statuscode 200: Success.
    """
    def get(self):
        self.write({'message': "PONG"})


class PongHandler(BaseHandler):
    """
    .. http:get:: /pong

       Route for in-depth health monitoring. This will check connections to all
       external services this one use.

       The `response` attribute may have one of three values.
           * `OK` indicates a healthy response.
           * `ERROR` indicates a connection or execution error.

       **Example request**:

       .. sourcecode:: http

          GET /pong HTTP/1.1

       **Example response**:

       .. sourcecode:: http

          HTTP/1.1 200 OK
          Vary: Accept
          Content-Type: text/javascript

            {
                "message": "OK",
                "services": {
                    "redis": {
                        "response": "OK",
                        "message": "PONG"
                        "response_time": 1
                    }
                }
            }

        :statuscode 200: Success.
        :statuscode 500: Internal server error. At least one service failed to
                        return a successful response.
    """
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
    """
    .. http:post:: /ticket

       Route for generating a new ticket.

       **Example request**:

       .. sourcecode:: http

          POST /ticket HTTP/1.1

       **Example response**:

       .. sourcecode:: http

          HTTP/1.1 200 OK
          Vary: Accept
          Content-Type: text/javascript

            {
                "ticket_id": "0D3KEBF3"
            }

        :param payload: String. Data to store as part of the ticket. Default
                        value '1'.
        :param ttl: Integer. The number of milliseconds for ticket to exist
                    before expiring. Default is 60 seconds (value of 60000).
        :statuscode 200: Success.
        :statuscode 400: Non-integer value passed for `ttl`. **TODO: NO HOOKS**
    """
    def post(self):
        payload = self.get_argument('payload', 1)
        ttl = self.get_int_value('ttl', self.DEFAULT_EXPIRATION)
        ticket_id = ticket_gen.get()
        self._generate_ticket(ticket_id, ttl, payload)
        self.write({'ticket_id': ticket_id})


class TicketIdHandler(BaseTicketHandler):
    def delete(self, ticket_id):
    """
    .. http:delete:: /ticket/(int:ticket_id)

       Route for Manually expiring a ticket by ID.

       **Example request**:

       .. sourcecode:: http

          DELETE /ticket/ABCDEF123 HTTP/1.1

       **Example response**:

       .. sourcecode:: http

          HTTP/1.1 200 OK
          Vary: Accept
          Content-Type: text/javascript

            {
                "message": "success"
            }

        :statuscode 200: Success.
    """
        self._delete_ticket(ticket_id)
        self.write({'message': "success"})

    def get(self, ticket_id):
    """
    .. http:get:: /ticket/(int:ticket_id)

       Route for getting the data associated with a ticket.

       **Example request**:

       .. sourcecode:: http

          GET /ticket/ABCDEF123 HTTP/1.1

       **Example response**:

       .. sourcecode:: http

          HTTP/1.1 200 OK
          Vary: Accept
          Content-Type: text/javascript

            {
                "payload": "1",
                "ticket_id": "ABCDEF123"
            }

        :param expire: Boolean. Indicates if fetching the ticket should be a
                       destructive action. Default to False.
        :statuscode 200: Success.
        :statuscode 400: Ticket does not exist. **TODO: NO HOOKS**
    """
        # Example/Test 400 response.
        if ticket_id == "RESERVED":
            raise tornado.web.HTTPError(
                status_code=400,
                reason="Reserved Key."
        )

        expire = self.get_argument('expire', False)
        payload = self._get_ticket(ticket_id, expire)
        self.write({'payload': payload, 'ticket_id': ticket_id})

    def put(self, ticket_id):
    """
    .. http:put:: /ticket/(int:ticket_id)

       Route for updating the data associated with a ticket and/or the TTL
       period for a ticket.

       **Example request**:

       .. sourcecode:: http

          PUT /ticket/ABCDEF123?payload=helloworld HTTP/1.1

       **Example response**:

       .. sourcecode:: http

          HTTP/1.1 200 OK
          Vary: Accept
          Content-Type: text/javascript

            {
                "message": "success"
            }

        :param payload: String. Data to store as part of the ticket. Default
                        value '1'.
        :param ttl: Integer. The number of milliseconds for ticket to exist
                    before expiring. Default is 60 seconds (value of 60000).
        :statuscode 200: Success.
        :statuscode 400: Non-integer value passed for `ttl`. **TODO: NO HOOKS**
        :statuscode 400: No `payload` or `ttl` parameter present in request.
    """
        payload = self.get_argument('payload', None)
        ttl = self.get_int_value('ttl', None)

        if payload and ttl:
            self._generate_ticket(ticket_id, ttl, payload)
        elif payload:
            self._update_ticket(ticket_id, payload=payload)
        elif ttl:
            self._update_ticket(ticket_id, ttl=ttl)
        else:
            raise tornado.web.HTTPError(
                status_code=400,
                reason="At least one argument required: 'payload', 'ttl'."
            )

        self.write({'message': "success"})


class VersionHandler(BaseHandler):
    def get(self):
    """
    .. http:get:: /ping

       Route for validating version of running application.

       **Example request**:

       .. sourcecode:: http

          GET /ping HTTP/1.1

       **Example response**:

       .. sourcecode:: http

          HTTP/1.1 200 OK
          Vary: Accept
          Content-Type: text/javascript

          {
              "version": "0.1.0"
          }

        :statuscode 200: Success.
    """
        self.write({'version': tickets.__version__})
