from django.db import models


class Lead(models.Model):
    SOURCES = [
        ("contacts", "Форма «Контакты»"),
        ("b2b", "Форма «Пробная партия»"),
    ]

    contact_name = models.CharField("ФИО", max_length=300)
    company = models.CharField("Компания", max_length=300, blank=True)
    phone = models.CharField("Телефон", max_length=50, blank=True)
    email = models.EmailField("Email")
    message = models.TextField("Сообщение", blank=True)
    source = models.CharField(
        "Источник", max_length=20, choices=SOURCES, default="contacts"
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Лид"
        verbose_name_plural = "Лиды"

    def __str__(self):
        return f"{self.contact_name} — {self.get_source_display()}"


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
