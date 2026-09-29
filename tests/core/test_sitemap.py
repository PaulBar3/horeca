import pytest


@pytest.mark.django_db
class TestSitemap:
    def test_sitemap_returns_200(self, client):
        response = client.get("/sitemap.xml")
        assert response.status_code == 200

    def test_sitemap_is_valid_xml(self, client):
        response = client.get("/sitemap.xml")
        content = response.content
        assert b"<urlset" in content
        assert b"</urlset>" in content

    def test_sitemap_contains_product_url(self, client, product):
        response = client.get("/sitemap.xml")
        assert product.get_absolute_url().encode() in response.content

    def test_sitemap_contains_published_article_url(self, client, article):
        response = client.get("/sitemap.xml")
        assert article.get_absolute_url().encode() in response.content

    def test_sitemap_contains_static_pages(self, client):
        response = client.get("/sitemap.xml")
        content = response.content
        assert b"/catalog/" in content
        assert b"/blog/" in content
