import pytest


@pytest.mark.django_db
class TestUiAssets:
    def test_font_css_linked(self, client):
        response = client.get("/")
        assert b"css/main.css" in response.content

    def test_sprite_icons_used(self, client):
        response = client.get("/")
        assert b"icons.svg#" in response.content

    def test_no_emoji_cart_in_header(self, client):
        response = client.get("/")
        assert "🛒".encode() not in response.content

    def test_usp_icons_replace_emoji(self, client):
        response = client.get("/")
        content = response.content
        for icon in (b"scale", b"clock", b"fire", b"cube", b"truck", b"banknotes"):
            assert f'#{icon}'.encode() in content or icon + b'"' in content
        for emoji in ("⚖️", "⏱️", "🛡️", "🏭", "🚚"):
            assert emoji.encode() not in content


@pytest.mark.django_db
class TestHomePageSections:
    def test_mockup_sections_present(self, client):
        content = client.get("/").content
        for text in (
            "Что мы готовим",
            "Часто всего",
            "Один продукт",
            "Удобно хранить",
            "Полуфабрикаты для HoReCa",
        ):
            assert text.encode() in content

    def test_header_has_phone_and_price_cta(self, client):
        content = client.get("/").content
        assert b"tel:+375291234567" in content
        assert "Получить прайс".encode() in content

    def test_no_reviews_section(self, client):
        content = client.get("/").content
        assert "Отзывы шеф-поваров".encode() not in content


BADGE = b'justify-center">'


@pytest.mark.django_db
class TestCartCountBadge:
    def _add(self, client, product, packaging, quantity):
        client.post("/orders/add/", {
            "product_id": product.pk,
            "packaging_id": packaging.pk,
            "quantity": quantity,
        })

    def test_badge_zero_when_empty(self, client):
        response = client.get("/")
        assert BADGE + b"0</span>" in response.content

    def test_badge_shows_count_on_page_load(self, client, product, packaging):
        self._add(client, product, packaging, 3)
        response = client.get("/")
        assert BADGE + b"3</span>" in response.content

    def test_badge_keeps_count_when_leaving_cart(self, client, product, packaging):
        self._add(client, product, packaging, 2)
        cart_page = client.get("/orders/")
        assert BADGE + b"2</span>" in cart_page.content
        home_page = client.get("/")
        assert BADGE + b"2</span>" in home_page.content
        catalog_page = client.get("/catalog/")
        assert BADGE + b"2</span>" in catalog_page.content
