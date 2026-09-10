from django.db import models


class Article(models.Model):
    CATEGORY_CHOICES = [
        ("recipe", "Рецепт"),
        ("news", "Новость"),
        ("tips", "Совет"),
    ]

    title = models.CharField("Заголовок", max_length=300)
    slug = models.SlugField("Slug", unique=True, allow_unicode=True)
    category = models.CharField("Категория", max_length=20, choices=CATEGORY_CHOICES)
    excerpt = models.TextField("Краткое описание", blank=True)
    content = models.TextField("Содержание")
    image = models.ImageField("Обложка", upload_to="blog/", blank=True)
    is_published = models.BooleanField("Опубликовано", default=False)
    published_at = models.DateTimeField("Дата публикации", null=True, blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self):
        return self.title
