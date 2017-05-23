
import tickets.app.cache as cache
import unittest
from unittest.mock import Mock, patch


class TestCacheMethods(unittest.TestCase):
    def setUp(self):
        # Reset cache client. Mock out the pool.
        cache._redis_client = None
        self.redis_client_pool = Mock()
        cache._redis_client_pool = self.redis_client_pool

    @patch('redis.Redis')
    def test_get_client(self, redis_mock):
        client = cache.get_client()

        assert client == redis_mock.return_value
        redis_mock.assert_called_with(connection_pool=self.redis_client_pool)

    @patch('tickets.app.cache.get_client')
    def test_ping(self, get_client_mock):
        client_mock = Mock()
        get_client_mock.return_value = client_mock
        resp = cache.ping()

        assert resp == client_mock.ping.return_value
        get_client_mock.assert_called_with()
        client_mock.ping.assert_called_with()
