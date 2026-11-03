import pytest

from core.models import Lead

MARKER = "Сайт готовится к открытию".encode()


def _enable(settings):
    settings.COMING_SOON = True


@pytest.mark.django_db
class TestClosedPages:
    @pytest.mark.parametrize("path", [
        "/",
        "/catalog/",
        "/blog/",
        "/blog/recipes/",
        "/b2b/",
        "/about/",
        "/contacts/",
    ])
    def test_path_serves_coming_soon(self, client, settings, path):
        _enable(settings)
        response = client.get(path)
        assert response.status_code == 200
        assert MARKER in response.content

    def test_product_detail_serves_coming_soon(self, client, settings, product):
        _enable(settings)
        response = client.get(product.get_absolute_url())
        assert response.status_code == 200
        assert MARKER in response.content

    def test_article_detail_serves_coming_soon(self, client, settings, article):
        _enable(settings)
        response = client.get(article.get_absolute_url())
        assert response.status_code == 200
        assert MARKER in response.content

    def test_coming_soon_is_noindex(self, client, settings):
        _enable(settings)
        response = client.get("/")
        assert b'name="robots" content="noindex"' in response.content

    def test_unknown_path_still_404(self, client, settings):
        _enable(settings)
        response = client.get("/net-takoy-stranicy/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestOpenPages:
    def test_admin_not_closed(self, client, settings):
        _enable(settings)
        response = client.get("/backend-admin/")
        assert response.status_code == 302
        assert MARKER not in response.content

    def test_cart_not_closed(self, client, settings):
        _enable(settings)
        response = client.get("/orders/")
        assert response.status_code == 200
        assert MARKER not in response.content

    def test_sitemap_not_closed(self, client, settings):
        _enable(settings)
        response = client.get("/sitemap.xml")
        assert response.status_code == 200
        assert MARKER not in response.content

    def test_robots_not_closed(self, client, settings):
        _enable(settings)
        response = client.get("/robots.txt")
        assert response.status_code == 200
        assert MARKER not in response.content


@pytest.mark.django_db
class TestClosedForms:
    def test_contact_post_creates_no_lead(self, client, settings):
        _enable(settings)
        response = client.post("/contacts/", {
            "contact_name": "Мария Сидорова",
            "email": "maria@mail.by",
            "message": "Здравствуйте",
        })
        assert response.status_code == 200
        assert MARKER in response.content
        assert Lead.objects.count() == 0

    def test_b2b_post_creates_no_lead(self, client, settings):
        _enable(settings)
        response = client.post("/b2b/trial-request/", {
            "contact_name": "Иван Иванов",
            "company": "Ресторан «Вкус»",
            "phone": "+375291111111",
            "email": "ivan@rest.by",
        })
        assert response.status_code == 200
        assert MARKER in response.content
        assert Lead.objects.count() == 0
