from decimal import Decimal

import pytest

from catalog.models import Packaging, Product, ProductImage
from orders.models import Order, OrderItem


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

    def test_create_order_saves_items(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 2,
        })
        client.post("/orders/create/", {
            "contact_name": "Тест Тестов",
            "company": "Тест ООО",
            "phone": "+375291234567",
            "email": "test@test.by",
        })
        order = Order.objects.get()
        assert order.items.count() == 1
        item = order.items.get()
        assert item.product == product
        assert item.packaging == packaging
        assert item.quantity == 2
        assert client.session.get("foodcore_cart") == {}

    def test_create_order_with_deleted_products(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 1,
        })
        Product.objects.all().delete()
        response = client.post("/orders/create/", {
            "contact_name": "Тест Тестов",
            "company": "Тест ООО",
            "phone": "+375291234567",
            "email": "test@test.by",
        })
        assert response.status_code == 302
        assert response.url.endswith("/orders/")
        assert Order.objects.count() == 0
        assert client.session.get("foodcore_cart") == {}

    def test_create_order_invalid_form_keeps_cart(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 1,
        })
        response = client.post("/orders/create/", {
            "contact_name": "Тест Тестов",
            "phone": "+375291234567",
            "email": "not-an-email",
        })
        assert response.status_code == 200
        assert Order.objects.count() == 0
        assert response.context["form"].errors.get("email")
        assert client.session.get("foodcore_cart")

    def test_order_success_page(self, client):
        response = client.get("/orders/success/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestOrderItemProtect:
    def test_cannot_delete_ordered_product(self, client, product, packaging):
        # Create an order that references the product
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 1,
        })
        client.post("/orders/create/", {
            "contact_name": "Тест Тестов",
            "phone": "+375291234567",
            "email": "test@test.by",
        })
        assert OrderItem.objects.filter(product=product).exists()

        # Deleting the product must be blocked to preserve order history
        from django.db.models import ProtectedError
        with pytest.raises(ProtectedError):
            product.delete()

    def test_can_delete_unordered_product(self, db, category):
        # A product with no order history can still be deleted
        p = Product.objects.create(name="Удаляемый", slug="udalyaemyi", category=category)
        p.delete()
        assert not Product.objects.filter(slug="udalyaemyi").exists()

    def test_field_error_shown_once_not_duplicated(self, client, product, packaging):
        # Regression: a summary block used to list every error AND each field
        # listed it again, so the same message appeared twice.
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 1,
        })
        response = client.post("/orders/create/", {
            "contact_name": "Тест Тестов",
            "phone": "+375291234567",
            "email": "not-an-email",
        })
        assert response.status_code == 200
        form = response.context["form"]
        error_text = form.errors["email"][0].encode()
        assert response.content.count(error_text) == 1


@pytest.mark.django_db
class TestResolveCartItems:
    def test_no_n_plus_one_for_multiple_items(self, category):
        from orders.views import _resolve_cart_items

        p1 = Product.objects.create(name="A", slug="a", category=category)
        p2 = Product.objects.create(name="B", slug="b", category=category)
        Packaging.objects.create(product=p1, weight_kg=1.0)
        Packaging.objects.create(product=p2, weight_kg=2.0)
        Packaging.objects.create(product=p2, weight_kg=5.0)

        cart = {
            str(p1.pk): {"packaging_id": p1.packagings.first().pk, "quantity": 1},
            str(p2.pk): {"packaging_id": p2.packagings.first().pk, "quantity": 2},
        }

        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        with CaptureQueriesContext(connection) as ctx:
            items = _resolve_cart_items(cart)

        assert len(items) == 2
        # 2 products + 2 packagings fetched in bulk; no per-item queries.
        # Allow a small constant overhead but far below a per-item N+1.
        assert len(ctx.captured_queries) <= 4
