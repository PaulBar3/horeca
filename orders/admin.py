from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "packaging", "quantity"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["pk", "contact_name", "company", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["contact_name", "company", "email", "phone"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [OrderItemInline]
    list_editable = ["status"]
