import logging

from django.contrib import messages
from django.shortcuts import render

from catalog.models import Product
from .models import Review

logger = logging.getLogger(__name__)


def home(request):
    featured_products = Product.objects.filter(is_featured=True).prefetch_related("images")[:4]
    new_products = Product.objects.filter(is_new=True).prefetch_related("images")[:4]
    reviews = Review.objects.filter(is_active=True)[:3]

    return render(request, "core/home.html", {
        "featured_products": featured_products,
        "new_products": new_products,
        "reviews": reviews,
    })


def contacts(request):
    if request.method == "POST":
        logger.info("Contact form submitted from %s", request.META.get("REMOTE_ADDR"))
        messages.success(
            request,
            "Сообщение отправлено. Мы ответим вам в ближайшее время.",
        )
    return render(request, "core/contacts.html")


def trial_request(request):
    if request.method == "POST":
        logger.info("Trial request submitted from %s", request.META.get("REMOTE_ADDR"))
        messages.success(
            request,
            "Ваш запрос отправлен. Мы свяжемся с вами в ближайшее время.",
        )
    return render(request, "core/b2b.html")
