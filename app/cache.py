
import redis
import ticketer.config


_redis_client = None
_redis_client_pool = None


def get_client():
    """Return a client from the pool."""
    global _redis_client
    global _redis_client_pool

    if _redis_client_pool is None:
        _redis_client_pool = redis.BlockingConnectionPool(**ticketer.config.REDIS)

    if _redis_client is None:
        _redis_client = redis.Redis(connection_pool=_redis_client_pool)

    return _redis_client


def ping():
    """Get a client and execute ping command."""
    get_client().ping()
