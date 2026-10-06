import logging

from django.contrib import messages
from django.db.models import Max
from django.shortcuts import render

from catalog.models import Category, Product

logger = logging.getLogger(__name__)


def home(request):
    featured_products = (
        Product.objects.filter(is_featured=True)
        .prefetch_related("images")
        .annotate(max_weight=Max("packagings__weight_kg"))[:4]
    )
    categories = Category.objects.all()

    return render(request, "core/home.html", {
        "featured_products": featured_products,
        "categories": categories,
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
