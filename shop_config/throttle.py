"""Lightweight, dependency-free per-IP request throttling.

Uses Django's default local-memory cache. Intentionally generous and
fail-open: it only ever blocks obvious hammering (dozens of POSTs a minute
from one IP) and never blocks a normal customer. Any internal error in the
throttling logic lets the request through rather than risk a false block on
a live storefront.

This guards the endpoints that create Stripe checkout sessions (real API
cost / abuse surface) and the file-upload customizer endpoints (CPU cost of
image/audio decoding) against cheap denial-of-service and Stripe API abuse.
"""
import functools

from django.core.cache import cache
from django.http import HttpResponse


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def throttle(*, limit=15, window=60, methods=("POST",)):
    """Allow at most `limit` requests per `window` seconds per client IP for
    the decorated view, counting only the given HTTP methods."""

    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method in methods:
                try:
                    key = f"throttle:{view_func.__name__}:{_client_ip(request)}"
                    count = cache.get(key, 0)
                    if count >= limit:
                        return HttpResponse(
                            "Příliš mnoho požadavků. Zkuste to prosím za chvíli.",
                            status=429,
                        )
                    # add() sets only if missing, so the window starts on the
                    # first hit; subsequent hits just increment.
                    if not cache.add(key, 1, window):
                        try:
                            cache.incr(key)
                        except ValueError:
                            cache.set(key, 1, window)
                except Exception:
                    # Fail open — never block a real customer over a cache hiccup.
                    pass
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
