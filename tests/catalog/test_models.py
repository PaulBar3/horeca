import pytest

from catalog.models import Category, Product


@pytest.fixture
def category(db):
    return Category.objects.create(
        name="Мясо",
        slug="meat",
        description="Мясные полуфабрикаты",
    )


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        name="Котлеты из говядины",
        slug="kotlety-govyadina",
        article="M-001",
        category=category,
        description="Сочные котлеты из говяжьего фарша",
        composition="Говядина, лук, специи",
        calories=250,
        protein=18.5,
        fat=15.0,
        carbs=8.0,
        shelf_life="5 дней",
        storage_conditions="от 0 до +4°C",
        meat_type="beef",
        cooking_method="frying",
    )


@pytest.mark.django_db
class TestCategory:
    def test_str(self, category):
        assert str(category) == "Мясо"

    def test_ordering(self):
        c1 = Category.objects.create(name="Рыба", slug="fish", order=2)
        c2 = Category.objects.create(name="Птица", slug="poultry", order=1)
        categories = list(Category.objects.all())
        assert categories[0] == c2
        assert categories[1] == c1


@pytest.mark.django_db
class TestProduct:
    def test_str(self, product):
        assert str(product) == "Котлеты из говядины"

    def test_get_main_image(self, product):
        assert product.get_main_image() is None

    def test_featured(self, product):
        assert not product.is_featured
        product.is_featured = True
        product.save()
        assert Product.objects.filter(is_featured=True).count() == 1

    def test_new(self, product):
        assert not product.is_new
        product.is_new = True
        product.save()
        assert Product.objects.filter(is_new=True).count() == 1


@pytest.mark.django_db
class TestPackaging:
    def test_str(self, product):
        from catalog.models import Packaging
        p = Packaging.objects.create(product=product, weight_kg=1.0)
        assert str(p) == "Котлеты из говядины — 1.0 кг"
