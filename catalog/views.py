from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Packaging, Product


def _apply_filters(queryset, params):
    q = params.get("q", "").strip()
    category_slug = params.get("category", "")
    meat_type = params.get("meat_type", "")
    cooking = params.get("cooking", "")
    packaging = params.get("packaging", "")

    valid_meat = {v for v, _ in Product.MEAT_TYPES if v}
    valid_cooking = {v for v, _ in Product.COOKING_METHODS if v}

    if q:
        queryset = queryset.filter(
            Q(name__icontains=q) | Q(article__icontains=q) | Q(description__icontains=q)
        )
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)
    if meat_type in valid_meat:
        queryset = queryset.filter(meat_type=meat_type)
    if cooking in valid_cooking:
        queryset = queryset.filter(cooking_method=cooking)
    if packaging:
        try:
            queryset = queryset.filter(packagings__weight_kg=Decimal(packaging))
        except InvalidOperation:
            pass

    return queryset.distinct(), q, category_slug, meat_type, cooking, packaging


def product_list(request):
    products = Product.objects.select_related("category").prefetch_related("images", "packagings")

    products, q, cat, meat, cook, pkg = _apply_filters(products, request.GET)

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "catalog/product_list.html", {
        "products": page_obj,
        "categories": Category.objects.all(),
        "meat_types": Product.MEAT_TYPES,
        "cooking_methods": Product.COOKING_METHODS,
        "packaging_options": (
            Packaging.objects.values_list("weight_kg", flat=True)
            .distinct().order_by("weight_kg")
        ),
        "is_paginated": page_obj.has_other_pages(),
        "page_obj": page_obj,
        "has_filters": bool(q or cat or meat or cook or pkg),
    })


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category")
        .prefetch_related("images", "packagings", "ttk_files"),
        slug=slug,
    )

    related_products = (
        Product.objects.filter(category=product.category)
        .exclude(pk=product.pk)
        .select_related("category")
        .prefetch_related("images", "packagings")[:4]
    )

    return render(request, "catalog/product_detail.html", {
        "product": product,
        "related_products": related_products,
    })
