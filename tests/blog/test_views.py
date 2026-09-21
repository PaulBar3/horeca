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
