import logging

from django.contrib import messages
from django.db.models import Max
from django.shortcuts import redirect, render

from catalog.models import Category, Product

from .forms import ContactForm, TrialRequestForm

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
    form = ContactForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            lead = form.save(commit=False)
            lead.source = "contacts"
            lead.save()
            logger.info("New lead #%d from contacts", lead.pk)
            messages.success(
                request,
                "Сообщение отправлено. Мы ответим вам в ближайшее время.",
            )
            return redirect("core:contacts")
    return render(request, "core/contacts.html", {"form": form})


def b2b(request):
    form = TrialRequestForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            lead = form.save(commit=False)
            lead.source = "b2b"
            lead.save()
            logger.info("New lead #%d from trial request", lead.pk)
            messages.success(
                request,
                "Ваш запрос отправлен. Мы свяжемся с вами в ближайшее время.",
            )
            return redirect("core:b2b")
    return render(request, "core/b2b.html", {"form": form})
