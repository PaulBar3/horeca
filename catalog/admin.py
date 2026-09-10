from django.contrib import admin

from config.mixins import SlugifyAdminMixin
from .models import Category, Product, ProductImage, Packaging, TTKFile


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class PackagingInline(admin.TabularInline):
    model = Packaging
    extra = 1


class TTKFileInline(admin.TabularInline):
    model = TTKFile
    extra = 1


@admin.register(Category)
class CategoryAdmin(SlugifyAdminMixin, admin.ModelAdmin):
    list_display = ["name", "slug", "order"]
    search_fields = ["name"]


@admin.register(Product)
class ProductAdmin(SlugifyAdminMixin, admin.ModelAdmin):
    list_display = [
        "name", "category", "article", "meat_type",
        "cooking_method", "is_featured", "is_new",
    ]
    list_filter = [
        "category", "meat_type", "cooking_method",
        "is_featured", "is_new",
    ]
    search_fields = ["name", "article", "description"]
    inlines = [ProductImageInline, PackagingInline, TTKFileInline]
    list_editable = ["is_featured", "is_new"]


@admin.register(Packaging)
class PackagingAdmin(admin.ModelAdmin):
    list_display = ["product", "weight_kg", "price_on_request"]
    list_filter = ["price_on_request"]
