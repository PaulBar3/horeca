import pytest


@pytest.mark.django_db
class TestArticleListView:
    def test_status_code(self, client):
        response = client.get("/blog/recipes/")
        assert response.status_code == 200

    def test_template(self, client):
        response = client.get("/blog/recipes/")
        assert "blog/article_list.html" in [t.name for t in response.templates]

    def test_filter_by_category(self, client, article):
        response = client.get("/blog/recipes/?category=recipe")
        assert response.status_code == 200

    def test_invalid_category_falls_back_to_recipe(self, client, article):
        # An unvalidated ?category= must not crash or leak; falls back to "recipe"
        response = client.get("/blog/recipes/?category=; DROP TABLE")
        assert response.status_code == 200
        assert "Тестовый рецепт".encode() in response.content

    def test_unknown_category_falls_back_to_recipe(self, client, article):
        response = client.get("/blog/recipes/?category=bogus")
        assert response.status_code == 200
        assert "Тестовый рецепт".encode() in response.content

    def test_card_shows_cover(self, client, article):
        article.image = "blog/cover.jpg"
        article.save()
        response = client.get("/blog/recipes/")
        assert b"/media/blog/cover.jpg" in response.content

    def test_card_without_cover(self, client, article):
        response = client.get("/blog/recipes/")
        assert b"/media/blog/" not in response.content


@pytest.mark.django_db
class TestBlogListView:
    def test_status_code(self, client):
        response = client.get("/blog/")
        assert response.status_code == 200

    def test_template(self, client):
        response = client.get("/blog/")
        assert "blog/blog_list.html" in [t.name for t in response.templates]


@pytest.mark.django_db
class TestArticleDetailView:
    def test_status_code(self, client, article):
        response = client.get("/blog/test-recept/")
        assert response.status_code == 200

    def test_404(self, client):
        response = client.get("/blog/nonexistent/")
        assert response.status_code == 404

    def test_detail_shows_cover_image(self, client, article):
        article.image = "blog/cover.jpg"
        article.save()
        response = client.get("/blog/test-recept/")
        assert b"/media/blog/cover.jpg" in response.content

    def test_detail_without_cover_no_img(self, client, article):
        response = client.get("/blog/test-recept/")
        assert b"/media/blog/" not in response.content
