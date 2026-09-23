from decimal import Decimal

import pytest

from catalog.models import Packaging, Product, ProductImage
from orders.models import Order


@pytest.mark.django_db
class TestCart:
    def test_empty_cart(self, client):
        response = client.get("/orders/")
        assert response.status_code == 200
        assert b'id="cart-items"' in response.content

    def test_add_to_cart(self, client, product, packaging):
        response = client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 2,
        })
        assert response.status_code == 200
        assert client.session.get("foodcore_cart", {}).get(str(product.pk))

    def test_cart_count(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 3,
        })
        response = client.get("/orders/count/")
        assert response.status_code == 200
        assert b"3" in response.content

    def test_remove_from_cart(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 1,
        })
        response = client.post(f"/orders/{product.pk}/remove/")
        assert response.status_code == 200
        assert str(product.pk) not in client.session.get("foodcore_cart", {})

    def test_increase_cart(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 2,
        })
        response = client.post(f"/orders/{product.pk}/increase/")
        assert response.status_code == 200
        assert client.session["foodcore_cart"][str(product.pk)]["quantity"] == 3

    def test_decrease_cart(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 3,
        })
        response = client.post(f"/orders/{product.pk}/decrease/")
        assert response.status_code == 200
        assert client.session["foodcore_cart"][str(product.pk)]["quantity"] == 2

    def test_decrease_cart_remove_when_zero(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 1,
        })
        response = client.post(f"/orders/{product.pk}/decrease/")
        assert response.status_code == 200
        assert str(product.pk) not in client.session.get("foodcore_cart", {})

    def test_add_missing_product_id(self, client):
        response = client.post("/orders/add/", {})
        assert response.status_code == 400

    def test_add_unknown_product(self, client):
        response = client.post("/orders/add/", {"product_id": 999999})
        assert response.status_code == 400
        assert not client.session.get("foodcore_cart")

    def test_add_returns_plain_count(self, client, product, packaging):
        response = client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 2,
        })
        assert response.content == b"2"

    def test_readd_updates_packaging(self, client, product, packaging):
        other = Packaging.objects.create(product=product, weight_kg=5.0)
        payload = {"product_id": product.pk, "quantity": 1}
        client.post("/orders/add/", {**payload, "packaging_id": packaging.pk})
        client.post("/orders/add/", {**payload, "packaging_id": other.pk})
        item = client.session["foodcore_cart"][str(product.pk)]
        assert item["packaging_id"] == other.pk

    def test_add_foreign_packaging(self, client, product, category):
        other_product = Product.objects.create(
            name="Другой", slug="drugoy", category=category, description="Д"
        )
        foreign = Packaging.objects.create(
            product=other_product, weight_kg=2.0
        )
        response = client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": foreign.pk,
        })
        assert response.status_code == 400

    def test_cart_page_renders_rows(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 2,
        })
        response = client.get("/orders/")
        assert b"cart-item-" in response.content

    def test_remove_renders_empty_rows(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 1,
        })
        response = client.post(f"/orders/{product.pk}/remove/")
        assert response.status_code == 200
        assert b"cart-item-" not in response.content
        assert b'hx-swap-oob="true"' in response.content

    def test_decrease_zero_renders_empty_rows(
        self, client, product, packaging
    ):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 1,
        })
        response = client.post(f"/orders/{product.pk}/decrease/")
        assert response.status_code == 200
        assert b"cart-item-" not in response.content
        assert str(product.pk) not in client.session.get("foodcore_cart", {})

    def test_cart_shows_price(self, client, product, packaging):
        product.price = Decimal("12.50")
        product.save()
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 2,
        })
        response = client.get("/orders/")
        assert b"12,50" in response.content
        assert b"25,00" in response.content

    def test_cart_price_on_request(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 1,
        })
        response = client.get("/orders/")
        assert "Цена по запросу".encode() in response.content

    def test_cart_sum_shown(self, client, product, packaging):
        product.price = Decimal("12.50")
        product.save()
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 2,
        })
        response = client.get("/orders/")
        i = response.content.find(b'id="cart-sum"')
        assert i != -1
        block = response.content[i:i + 500]
        assert "Итого".encode() in block
        assert b"25,00" in block

    def test_cart_sum_on_request(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 1,
        })
        response = client.get("/orders/")
        i = response.content.find(b'id="cart-sum"')
        assert i != -1
        block = response.content[i:i + 500]
        assert "Цена по запросу".encode() in block

    def test_cart_sum_oob_on_change(self, client, product, packaging):
        product.price = Decimal("10.00")
        product.save()
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 1,
        })
        response = client.post(f"/orders/{product.pk}/increase/")
        i = response.content.find(b'id="cart-sum"')
        assert i != -1
        block = response.content[i:i + 300]
        assert b'hx-swap-oob="true"' in block
        assert b"20,00" in block

    def test_cart_row_shows_image(self, client, product, packaging):
        ProductImage.objects.create(product=product, image="products/cart.jpg", is_main=True)
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 1,
        })
        response = client.get("/orders/")
        assert b"/media/products/cart.jpg" in response.content

    def test_cart_row_without_image(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 1,
        })
        response = client.get("/orders/")
        assert b"/media/products" not in response.content

    def test_cart_row_shows_packaging_description(self, client, product, packaging):
        packaging.description = "≈50 шт в горсти"
        packaging.save()
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 1,
        })
        response = client.get("/orders/")
        assert "(≈50 шт в горсти)".encode() in response.content

    def test_cart_row_without_packaging_description(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 1,
        })
        response = client.get("/orders/")
        assert b"1,00 \xd0\xba\xd0\xb3</p>" in response.content
        assert "≈".encode() not in response.content


@pytest.mark.django_db
class TestOrder:
    def test_create_order(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 2,
        })
        response = client.post("/orders/create/", {
            "contact_name": "Тест Тестов",
            "company": "Тест ООО",
            "phone": "+375291234567",
            "email": "test@test.by",
            "comment": "Тестовый заказ",
        })
        assert response.status_code == 302
        assert Order.objects.count() == 1

    def test_order_success_page(self, client):
        response = client.get("/orders/success/")
        assert response.status_code == 200
