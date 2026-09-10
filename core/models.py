from django.db import models


class Review(models.Model):
    author_name = models.CharField("Имя", max_length=200)
    author_position = models.CharField("Должность", max_length=300, blank=True)
    author_company = models.CharField("Компания / Ресторан", max_length=300, blank=True)
    text = models.TextField("Текст отзыва")
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"{self.author_name} — {self.author_company}"
