"""
Security middleware for FOODCORE.
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
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # {path: {(ip, timestamp_bucket): count}}
        self._hits = defaultdict(lambda: defaultdict(int))
        self._cleanup_interval = 300
        self._last_cleanup = time.time()

    def __call__(self, request):
        if request.method == "POST":
            rate_limits = getattr(settings, "RATE_LIMITS", {})
            path = request.path

            for limit_path, (max_requests, window) in rate_limits.items():
                if path.startswith(limit_path):
                    ip = self._get_client_ip(request)
                    now = time.time()
                    bucket = int(now / window)
                    key = (ip, bucket)

                    self._hits[limit_path][key] += 1

                    if now - self._last_cleanup > self._cleanup_interval:
                        self._cleanup(now, window)
                        self._last_cleanup = now

                    if self._hits[limit_path][key] > max_requests:
                        return JsonResponse(
                            {"error": "Слишком много запросов. Попробуйте позже."},
                            status=429,
                        )
                    break

        return self.get_response(request)

    def _get_client_ip(self, request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "0.0.0.0")

    def _cleanup(self, now, window):
        cutoff_bucket = int(now / window) - 2
        for path in list(self._hits):
            for key in list(self._hits[path]):
                if key[1] < cutoff_bucket:
                    del self._hits[path][key]
            if not self._hits[path]:
                del self._hits[path]
