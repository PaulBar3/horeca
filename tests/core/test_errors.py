import pytest
from django.template.loader import render_to_string
from django.test import Client


@pytest.mark.django_db
class TestNotFoundPage:
    def test_unknown_url_returns_404(self, client):
        response = client.get("/net-takoy-stranicy/")
        assert response.status_code == 404

    def test_404_uses_styled_template(self, client):
        response = client.get("/net-takoy-stranicy/")
        content = response.content
        assert "Страница не найдена".encode() in content
        assert b"FOODBASE" in content
        assert b"/net-takoy-stranicy/" in content

    def test_404_has_navigation_links(self, client):
        response = client.get("/net-takoy-stranicy/")
        content = response.content
        assert ">На главную<".encode() in content
        assert ">В каталог<".encode() in content


class TestServerErrorPage:
    def test_500_uses_styled_template(self):
        # Django renders 500.html without context (template.render())
        body = render_to_string("500.html")
        assert "Что-то пошло не так".encode() in body.encode()
        assert "FOODBASE" in body

    def test_500_has_navigation_links(self):
        body = render_to_string("500.html")
        assert ">На главную<" in body
        assert ">В каталог<" in body


@pytest.mark.django_db
class TestCsrfForbiddenPage:
    def test_csrf_failure_returns_403(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post("/orders/create/", {"contact_name": "x"})
        assert response.status_code == 403

    def test_csrf_failure_uses_styled_template(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post("/orders/create/", {"contact_name": "x"})
        content = response.content
        assert "Доступ запрещён".encode() in content
        assert b"FOODBASE" in content
        assert b"CSRF verification failed" not in content

    def test_csrf_failure_has_navigation_links(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post("/orders/create/", {"contact_name": "x"})
        content = response.content
        assert ">На главную<".encode() in content
        assert ">В каталог<".encode() in content


class TestBadRequestPage:
    def test_400_uses_styled_template(self):
        # bad_request renders 400.html with request only (no exception context)
        body = render_to_string("400.html")
        assert "Некорректный запрос".encode() in body.encode()
        assert "FOODBASE" in body

    def test_400_has_navigation_links(self):
        body = render_to_string("400.html")
        assert ">На главную<" in body
        assert ">В каталог<" in body


class TestPermissionDeniedPage:
    def test_403_uses_styled_template(self):
        body = render_to_string("403.html")
        assert "Доступ запрещён".encode() in body.encode()
        assert "FOODBASE" in body

    def test_403_has_navigation_links(self):
        body = render_to_string("403.html")
        assert ">На главную<" in body
        assert ">В каталог<" in body
