import pytest

from catalog.models import Product, ProductImage


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

    def test_pagination_preserves_query(self, client, category):
        for i in range(13):
            Product.objects.create(
                name=f"Товар {i}", slug=f"tovar-{i}", category=category, description="Описание"
            )
        response = client.get("/catalog/?q=Товар")
        assert b"q=%D0%A2%D0%BE%D0%B2%D0%B0%D1%80&amp;page=2" in response.content

    def test_pagination_marks_current_page(self, client, category):
        for i in range(13):
            Product.objects.create(
                name=f"Товар {i}", slug=f"tovar-{i}", category=category, description="Описание"
            )
        response = client.get("/catalog/?q=Товар&page=2")
        assert b'aria-current="page"' in response.content

    def test_card_shows_main_image(self, client, product):
        ProductImage.objects.create(product=product, image="products/test.jpg", is_main=True)
        response = client.get("/catalog/")
        assert b"/media/products/test.jpg" in response.content

    def test_card_without_image_keeps_placeholder(self, client, product):
        response = client.get("/catalog/")
        assert b"/media/products" not in response.content
        assert b"aspect-square" in response.content


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

    def test_detail_single_image(self, client, product):
        ProductImage.objects.create(product=product, image="products/a.jpg", is_main=True)
        response = client.get("/catalog/kotlety/")
        assert b"/media/products/a.jpg" in response.content

    def test_detail_multiple_images_grid(self, client, product):
        ProductImage.objects.create(product=product, image="products/a.jpg", is_main=True)
        ProductImage.objects.create(product=product, image="products/b.jpg")
        response = client.get("/catalog/kotlety/")
        assert b"/media/products/a.jpg" in response.content
        assert b"/media/products/b.jpg" in response.content
        assert b"grid-cols-2" in response.content

    def test_detail_without_image(self, client, product):
        response = client.get("/catalog/kotlety/")
        assert b"/media/products" not in response.content
        assert b"aspect-square" in response.content

    def test_packaging_description_in_select(self, client, product, packaging):
        packaging.description = "≈50 шт в горсти"
        packaging.save()
        response = client.get("/catalog/kotlety/")
        assert "1,00 кг — ≈50 шт в горсти".encode() in response.content

    def test_packaging_without_description(self, client, product, packaging):
        response = client.get("/catalog/kotlety/")
        assert b">1,00 \xd0\xba\xd0\xb3</option>" in response.content
        assert b"1,00 \xd0\xba\xd0\xb3 \xe2\x80\x94" not in response.content
