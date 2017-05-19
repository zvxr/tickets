# Changelog
For core tickets service.

## [Unreleased]
- [ ] Handle arguments for existing routes.
- [ ] Add unit testing.
- [ ] Add documentation.
- [ ] Add route `PUT /ticket/:id?payload=&ttl=`.
- [ ] Add route `DELETE /ticket/:id`.
- [ ] Generate build script.
- [ ] Add webhooks.

## [0.1.0] - 2017-05-19
- Added core Tornado application.
- Added handlers for `POST /ticket`, `GET /ticket/:ticket_id`, `GET /ping`, `GET /pong`, and `GET /version`.
- Added Redis cache and connection pool manager.
- Added rudimentary ticket generator.
- Added `Dockerfile`, `setup.py`, `requirements.txt`, and demo executable.
