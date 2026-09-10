import pytest

from orders.models import Order


@pytest.mark.django_db
class TestCart:
    def test_empty_cart(self, client):
        response = client.get("/orders/")
        assert response.status_code == 200

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

    def test_update_cart(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 3,
        })
        response = client.post(f"/orders/{product.pk}/update/", {"delta": -1})
        assert response.status_code == 200
        assert client.session["foodcore_cart"][str(product.pk)]["quantity"] == 2

    def test_update_cart_remove_when_zero(self, client, product, packaging):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": 1,
        })
        response = client.post(f"/orders/{product.pk}/update/", {"delta": -1})
        assert response.status_code == 200
        assert str(product.pk) not in client.session.get("foodcore_cart", {})


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
