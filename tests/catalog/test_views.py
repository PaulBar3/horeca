import pytest

from catalog.models import Product


@pytest.mark.django_db
class TestProductListView:
    def test_status_code(self, client):
        response = client.get("/catalog/")
        assert response.status_code == 200

    def test_template(self, client):
        response = client.get("/catalog/")
        assert "catalog/product_list.html" in [t.name for t in response.templates]

    def test_filter_by_category(self, client, category, product):
        response = client.get("/catalog/?category=meat")
        assert response.status_code == 200

    def test_search(self, client, product):
        response = client.get("/catalog/?q=котлет")
        assert response.status_code == 200


@pytest.mark.django_db
class TestProductDetailView:
    def test_status_code(self, client, product):
        response = client.get("/catalog/kotlety/")
        assert response.status_code == 200

    def test_404(self, client):
        response = client.get("/catalog/nonexistent/")
        assert response.status_code == 404

    def test_template(self, client, product):
        response = client.get("/catalog/kotlety/")
        assert "catalog/product_detail.html" in [t.name for t in response.templates]
