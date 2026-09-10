from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.cart_view, name="cart"),
    path("add/", views.cart_add, name="cart_add"),
    path("<int:product_id>/update/", views.cart_update, name="cart_update"),
    path("<int:product_id>/remove/", views.cart_remove, name="cart_remove"),
    path("count/", views.cart_count, name="cart_count"),
    path("create/", views.order_create, name="order_create"),
    path("success/", views.order_success, name="order_success"),
]
