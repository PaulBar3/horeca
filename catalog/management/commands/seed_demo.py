"""Seed demo catalog data matching the homepage design mockup."""

from django.core.management.base import BaseCommand

from catalog.models import Category, Packaging, Product

CATEGORIES = [
    {"name": "Курица", "slug": "kurica", "order": 1,
     "description": "Крыло · бедро · филе · голень"},
    {"name": "Свинина", "slug": "svinina", "order": 2,
     "description": "Шея · лопатка · корейка · стейки"},
    {"name": "Шашлык", "slug": "shashlyk", "order": 3,
     "description": "Порционные заготовки в маринадах"},
    {"name": "Фарш / Рубленые изделия", "slug": "farsh", "order": 4,
     "description": "Котлеты · биточки · заготовки"},
]

PRODUCTS = [
    {"name": "Шашлык из свиной шеи", "slug": "shashlyk-iz-svinoy-shei",
     "category": "shashlyk", "meat_type": "pork",
     "composition": "Маринад: Красное песто",
     "description": "Порционные заготовки из свиной шеи в насыщенном красном маринаде."},
    {"name": "Куриное бедро", "slug": "kurinoe-bedro",
     "category": "kurica", "meat_type": "chicken",
     "composition": "Маринад: Гриль",
     "description": "Охлаждённое бедро курицы в маринаде «Гриль», готово к быстрой готовке."},
    {"name": "Корейка свинная", "slug": "koreyka-svinaya",
     "category": "svinina", "meat_type": "pork",
     "composition": "Маринад: Лимонный перец",
     "description": "Стейки из корейки в маринаде с лимонным перцем."},
    {"name": "Куриное филе", "slug": "kurinoe-file",
     "category": "kurica", "meat_type": "chicken",
     "composition": "Маринад: Базис",
     "description": "Филе куриной грудки в универсальном маринаде «Базис»."},
]

JUNK_CATEGORIES = ["test", "meat-dbg"]
JUNK_PRODUCTS = ["nazvanie-test", "testfas"]


class Command(BaseCommand):
    help = "Create demo categories/products for the homepage design (idempotent)"

    def handle(self, *args, **options):
        deleted_cats, _ = Category.objects.filter(slug__in=JUNK_CATEGORIES).delete()
        deleted_prods, _ = Product.objects.filter(slug__in=JUNK_PRODUCTS).delete()
        self.stdout.write(f"Удалено мусора: категорий {deleted_cats}, объектов {deleted_prods}")

        for fields in CATEGORIES:
            Category.objects.update_or_create(slug=fields["slug"], defaults=fields)

        for fields in PRODUCTS:
            category = Category.objects.get(slug=fields["category"])
            product, _created = Product.objects.update_or_create(
                slug=fields["slug"],
                defaults={**fields, "category": category, "is_featured": True},
            )
            Packaging.objects.get_or_create(product=product, weight_kg=3.00)

        total = Product.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"Готово: {Category.objects.count()} категорий, {total} товаров "
            f"(featured: {Product.objects.filter(is_featured=True).count()})"
        ))
