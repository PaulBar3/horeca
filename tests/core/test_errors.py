import pytest
from django.template.loader import render_to_string


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
