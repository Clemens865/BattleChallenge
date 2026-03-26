"""Middleware package.

All middleware classes follow the same pattern:
  - before(request) -> None or response dict
  - after(request, response) -> response dict

If before() returns a response dict, the request is short-circuited
(no further middleware or handler is called).
"""
