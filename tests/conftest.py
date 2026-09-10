import pytest
from django.test import Client

from blog.models import Article
from catalog.models import Category, Packaging, Product


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def category(db):
    return Category.objects.create(name="Мясо", slug="meat")


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        name="Котлеты",
        slug="kotlety",
        category=category,
        description="Описание котлет",
        is_featured=True,
    )


@pytest.fixture
def packaging(db, product):
    return Packaging.objects.create(product=product, weight_kg=1.0)


@pytest.fixture
def article(db):
    return Article.objects.create(
        title="Тестовый рецепт",
        slug="test-recept",
        category="recipe",
        content="Содержание статьи",
        is_published=True,
    )
