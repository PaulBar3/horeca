from django.contrib import admin

from config.mixins import SlugifyAdminMixin
from .models import Article


@admin.register(Article)
class ArticleAdmin(SlugifyAdminMixin, admin.ModelAdmin):
    slugify_from = "title"
    list_display = ["title", "category", "is_published", "published_at"]
    list_filter = ["category", "is_published"]
    search_fields = ["title", "content"]
    list_editable = ["is_published"]
