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
        for icon in (b"scale", b"clock", b"shield-check", b"cog-6-tooth", b"truck", b"fire"):
            assert f'#{icon}'.encode() in content or icon + b'"' in content
        for emoji in ("⚖️", "⏱️", "🛡️", "🏭", "🚚"):
            assert emoji.encode() not in content
