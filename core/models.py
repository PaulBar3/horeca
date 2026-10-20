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
