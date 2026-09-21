from django.db import models


class Category(models.Model):
    name = models.CharField("Название", max_length=200)
    slug = models.SlugField("Slug", unique=True, allow_unicode=True)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="categories/", blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    MEAT_TYPES = [
        ("", "Не указано"),
        ("beef", "Говядина"),
        ("pork", "Свинина"),
        ("chicken", "Курица"),
        ("turkey", "Индейка"),
        ("fish", "Рыба"),
    ]

    COOKING_METHODS = [
        ("", "Не указано"),
        ("frying", "Жарка"),
        ("boiling", "Варка"),
        ("baking", "Запекание"),
        ("steaming", "На пару"),
    ]

    name = models.CharField("Название", max_length=300)
    slug = models.SlugField("Slug", unique=True, allow_unicode=True)
    article = models.CharField("Артикул", max_length=50, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Категория",
    )
    description = models.TextField("Описание")
    composition = models.TextField("Состав", blank=True)
    price = models.DecimalField(
        "Цена (BYN)", max_digits=10, decimal_places=2, null=True, blank=True
    )
    calories = models.PositiveIntegerField(
        "Калорийность (ккал/100г)", null=True, blank=True
    )
    protein = models.DecimalField(
        "Белки (г)", max_digits=5, decimal_places=2, null=True, blank=True
    )
    fat = models.DecimalField(
        "Жиры (г)", max_digits=5, decimal_places=2, null=True, blank=True
    )
    carbs = models.DecimalField(
        "Углеводы (г)", max_digits=5, decimal_places=2, null=True, blank=True
    )
    shelf_life = models.CharField("Срок годности", max_length=200, blank=True)
    storage_conditions = models.CharField("Условия хранения", max_length=300, blank=True)
    meat_type = models.CharField("Тип мяса", max_length=20, choices=MEAT_TYPES, blank=True)
    cooking_method = models.CharField(
        "Способ приготовления", max_length=20, choices=COOKING_METHODS, blank=True
    )
    is_featured = models.BooleanField("Рекомендуемый", default=False)
    is_new = models.BooleanField("Новинка", default=False)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name

    def get_main_image(self):
        return self.images.filter(is_main=True).first() or self.images.first()  # pylint: disable=no-member


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Товар",
    )
    image = models.ImageField("Изображение", upload_to="products/")
    alt = models.CharField("ALT", max_length=300, blank=True)
    is_main = models.BooleanField("Главное фото", default=False)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Фото товара"
        verbose_name_plural = "Фото товаров"

    def __str__(self):
        return f"Фото {self.product.name} ({self.order})"


class Packaging(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="packagings",
        verbose_name="Товар",
    )
    weight_kg = models.DecimalField("Вес (кг)", max_digits=6, decimal_places=2)
    price_on_request = models.BooleanField("Цена по запросу", default=True)

    class Meta:
        ordering = ["weight_kg"]
        verbose_name = "Фасовка"
        verbose_name_plural = "Фасовки"

    def __str__(self):
        return f"{self.product.name} — {self.weight_kg} кг"


class TTKFile(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="ttk_files",
        verbose_name="Товар",
    )
    title = models.CharField("Название файла", max_length=300)
    pdf = models.FileField("PDF-файл", upload_to="ttk/")

    class Meta:
        verbose_name = "ТТК"
        verbose_name_plural = "ТТК"

    def __str__(self):
        return f"{self.product.name} — {self.title}"
