from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Новая"),
        ("processing", "В обработке"),
        ("completed", "Завершена"),
        ("cancelled", "Отменена"),
    ]

    contact_name = models.CharField("ФИО", max_length=300)
    company = models.CharField("Компания", max_length=300, blank=True)
    phone = models.CharField("Телефон", max_length=50)
    email = models.EmailField("Email")
    comment = models.TextField("Комментарий", blank=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField("Создана", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлена", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return f"Заявка #{self.pk} от {self.contact_name}"

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заявка",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        verbose_name="Товар",
    )
    packaging = models.ForeignKey(
        "catalog.Packaging",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Фасовка",
    )
    quantity = models.PositiveIntegerField("Количество", default=1)

    class Meta:
        verbose_name = "Позиция заявки"
        verbose_name_plural = "Позиции заявок"

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
