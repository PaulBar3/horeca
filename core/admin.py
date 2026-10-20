from django.contrib import admin

from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["contact_name", "company", "email", "phone", "source", "created_at"]
    list_filter = ["source", "created_at"]
    search_fields = ["contact_name", "company", "email", "phone", "message"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"
