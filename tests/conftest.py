import pytest

from blog.models import Article
from catalog.models import Category, Packaging, Product


@pytest.fixture(autouse=True)
def coming_soon_off(settings):
    """Existing tests exercise the real pages; coming-soon tests opt in."""
    settings.COMING_SOON = False


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
