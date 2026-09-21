from django.contrib import admin

from config.mixins import SlugifyAdminMixin
from .models import Article


@admin.register(Article)
class ArticleAdmin(SlugifyAdminMixin, admin.ModelAdmin):
    slugify_from = "title"
    list_display = ["title", "category", "is_published", "published_at"]
    list_display_links = ["title"]
    list_filter = ["category", "is_published"]
    search_fields = ["title", "content"]
    list_editable = ["is_published"]
    date_hierarchy = "published_at"
    save_on_top = True
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        ("Основное", {
            "fields": ["title", "slug", "category", "image"],
        }),
        ("Содержание", {
            "fields": ["excerpt", "content"],
        }),
        ("Публикация", {
            "fields": ["is_published", "published_at", "created_at", "updated_at"],
        }),
    ]

    class Media:
        js = ("admin/js/slugify.js",)
