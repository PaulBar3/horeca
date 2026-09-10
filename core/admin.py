from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["author_name", "author_company", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_filter = ["is_active"]
