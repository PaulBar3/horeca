import pytest
from django.http import HttpResponse
from django.test import RequestFactory, override_settings

from config.middleware import RateLimitMiddleware


def _get_response(request):
    return HttpResponse("ok")


def _make_request(path="/orders/create/", ip="1.2.3.4", xff=None):
    request = RequestFactory().post(path, data={})
    request.META["REMOTE_ADDR"] = ip
    if xff is not None:
        request.META["HTTP_X_FORWARDED_FOR"] = xff
    return request


@pytest.mark.django_db
class TestRateLimit:
    @override_settings(RATE_LIMITS={"/orders/create/": (2, 60)}, RATE_LIMIT_MAX_KEYS=5000)
    def test_under_limit_passes(self):
        mw = RateLimitMiddleware(_get_response)
        for _ in range(2):
            assert mw(_make_request()).status_code == 200

    @override_settings(RATE_LIMITS={"/orders/create/": (2, 60)}, RATE_LIMIT_MAX_KEYS=5000)
    def test_over_limit_returns_429(self):
        mw = RateLimitMiddleware(_get_response)
        for _ in range(2):
            mw(_make_request())
        response = mw(_make_request())
        assert response.status_code == 429
        assert response["Content-Type"].startswith("application/json")

    @override_settings(RATE_LIMITS={"/orders/create/": (2, 60)}, RATE_LIMIT_MAX_KEYS=5000)
    def test_spoofed_xff_first_value_bypasses_nothing(self):
        # Different spoofed FIRST values, same real (last) value share one limit.
        mw = RateLimitMiddleware(_get_response)
        for spoof in ("10.0.0.1", "10.0.0.2", "10.0.0.3"):
            response = mw(_make_request(xff=f"{spoof}, 9.9.9.9"))
        assert response.status_code == 429

    @override_settings(RATE_LIMITS={"/orders/create/": (2, 60)}, RATE_LIMIT_MAX_KEYS=5000)
    def test_keys_on_last_xff_value(self):
        mw = RateLimitMiddleware(_get_response)
        mw(_make_request(xff="1.1.1.1, 2.2.2.2, 9.9.9.9"))
        mw(_make_request(xff="8.8.8.8, 9.9.9.9"))
        assert mw(_make_request(xff="7.7.7.7, 9.9.9.9")).status_code == 429
        # A different real (last) IP still has its own budget
        assert mw(_make_request(xff="6.6.6.6, 5.5.5.5")).status_code == 200

    @override_settings(RATE_LIMITS={"/orders/create/": (2, 60)}, RATE_LIMIT_MAX_KEYS=5000)
    def test_falls_back_to_remote_addr(self):
        mw = RateLimitMiddleware(_get_response)
        for _ in range(2):
            mw(_make_request(ip="4.4.4.4"))
        assert mw(_make_request(ip="4.4.4.4")).status_code == 429


@pytest.mark.django_db
class TestRateLimitCap:
    @override_settings(RATE_LIMITS={"/x/": (100, 60)}, RATE_LIMIT_MAX_KEYS=5)
    def test_cap_bounds_tracked_keys(self):
        mw = RateLimitMiddleware(_get_response)
        for i in range(50):
            mw(_make_request(path="/x/", xff=f"10.0.0.{i}"))
        # Only the first 5 distinct keys are tracked; the rest are ignored
        assert len(mw._hits["/x/"]) <= 5

    @override_settings(RATE_LIMITS={"/x/": (2, 60)}, RATE_LIMIT_MAX_KEYS=1)
    def test_existing_keys_still_counted_beyond_cap(self):
        mw = RateLimitMiddleware(_get_response)
        mw(_make_request(path="/x/", xff="9.9.9.9"))
        mw(_make_request(path="/x/", xff="9.9.9.9"))
        # New IP is ignored (cap reached), but the tracked one still limits
        mw(_make_request(path="/x/", xff="8.8.8.8"))
        assert mw(_make_request(path="/x/", xff="9.9.9.9")).status_code == 429
