
import os


APP_PORT = os.getenv('APP_PORT', 8080)

# When linking web application to Redis, environment variables will be formed based off of this
# name. Example: `--link redis:cache` will yield CACHE_* for Redis related env variables.
REDIS_ALIAS = "CACHE"
REDIS_PORT = os.getenv('{alias}_PORT'.format(alias=REDIS_ALIAS), 6379).split(':')[-1]
REDIS = {
    'host': os.getenv(
        '{alias}_PORT_{port}_TCP_ADDR'.format(alias=REDIS_ALIAS, port=REDIS_PORT),
        "localhost"
    ),
    'port': REDIS_PORT
}
