"""
Security middleware for FOODBASE.
"""

import time
from collections import defaultdict

from django.http import JsonResponse
from django.conf import settings


class RateLimitMiddleware:
    """
    Simple in-memory rate limiter for POST endpoints.

    Configure via RATE_LIMITS dict in settings:
        RATE_LIMITS = {
            "/orders/create/": (5, 60),      # 5 requests per 60 seconds
            "/contacts/": (3, 60),            # 3 requests per 60 seconds
            "/b2b/": (3, 60),                 # 3 requests per 60 seconds
            "/orders/add/": (30, 60),         # 30 requests per 60 seconds
        }

    RATE_LIMIT_MAX_KEYS caps how many (ip, bucket) keys are tracked per path
    so a flood of distinct keys cannot grow memory without bound.

    Known limitation: the counters are in-process and therefore per gunicorn
    worker. With several sync workers the effective limit is divided between
    them (best-effort). Fixing that would require a shared store (Redis/DB),
    which is out of scope for this project.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # {path: {(ip, timestamp_bucket): count}}
        self._hits = defaultdict(dict)
        # {path: window_seconds} — remembered so cleanup uses each path's own window
        self._windows = {}
        self._cleanup_interval = 300
        self._last_cleanup = time.time()

    def __call__(self, request):
        if request.method == "POST":
            rate_limits = getattr(settings, "RATE_LIMITS", {})
            max_keys = getattr(settings, "RATE_LIMIT_MAX_KEYS", 5000)
            path = request.path

            for limit_path, (max_requests, window) in rate_limits.items():
                if path.startswith(limit_path):
                    now = time.time()
                    ip = self._get_client_ip(request)
                    bucket = int(now / window)
                    key = (ip, bucket)

                    if now - self._last_cleanup > self._cleanup_interval:
                        self._cleanup(now)
                        self._last_cleanup = now

                    store = self._hits[limit_path]
                    self._windows[limit_path] = window

                    if key not in store and len(store) >= max_keys:
                        # Cap reached: do not track new keys (fail-open for
                        # unknown IPs) so memory stays bounded. Existing keys
                        # keep being counted.
                        break

                    store[key] = store.get(key, 0) + 1

                    if store[key] > max_requests:
                        return JsonResponse(
                            {"error": "Слишком много запросов. Попробуйте позже."},
                            status=429,
                        )
                    break

        return self.get_response(request)

    def _get_client_ip(self, request):
        # Trust the LAST entry in X-Forwarded-For: it is the one appended by
        # our reverse proxy (Caddy), which is the only entry point. Everything
        # before it is client-controlled and must not be trusted, otherwise the
        # limit is trivially bypassed by rotating a spoofed first value.
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            parts = [part.strip() for part in x_forwarded.split(",") if part.strip()]
            if parts:
                return parts[-1]
        return request.META.get("REMOTE_ADDR", "0.0.0.0")

    def _cleanup(self, now):
        for path in list(self._hits):
            window = self._windows.get(path, 60)
            cutoff_bucket = int(now / window) - 2
            for key in list(self._hits[path]):
                if key[1] < cutoff_bucket:
                    del self._hits[path][key]
            if not self._hits[path]:
                del self._hits[path]
                self._windows.pop(path, None)
