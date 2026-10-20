from django.contrib import admin

from .models import Lead, Review


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["contact_name", "company", "email", "phone", "source", "created_at"]
    list_filter = ["source", "created_at"]
    search_fields = ["contact_name", "company", "email", "phone", "message"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["author_name", "author_company", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_filter = ["is_active"]
