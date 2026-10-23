import logging

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from catalog.models import Packaging, Product

from .cart import (
    CART_MAX_QUANTITY,
    cart_total,
    get_cart,
    parse_int,
    parse_quantity,
    save_cart,
)
from .forms import OrderForm
from .models import OrderItem

logger = logging.getLogger(__name__)


def _resolve_cart_items(cart_data):
    if not cart_data:
        return []

    product_ids = []
    packaging_ids = []
    for product_id, item_data in cart_data.items():
        product_ids.append(product_id)
        pid = item_data.get("packaging_id")
        if pid:
            packaging_ids.append(pid)

    products = {
        p.pk: p
        for p in Product.objects.filter(pk__in=product_ids).prefetch_related(
            "packagings"
        )
    }
    packagings = {p.pk: p for p in Packaging.objects.filter(pk__in=packaging_ids)}

    items = []
    for product_id, item_data in cart_data.items():
        product = products.get(int(product_id)) if str(product_id).isdigit() else None
        if product is None:
            continue

        packaging = None
        packaging_id = item_data.get("packaging_id")
        if packaging_id and int(packaging_id) in packagings:
            packaging = packagings[int(packaging_id)]

        quantity = item_data.get("quantity", 1)
        items.append({
            "product": product,
            "packaging": packaging or product.packagings.first(),
            "quantity": quantity,
            "unit_price": product.price,
            "line_total": product.price * quantity if product.price else None,
        })
    return items


def _price_totals(items):
    """Sum of priced positions and flag for priceless ones."""
    line_totals = [item["line_total"] for item in items if item["line_total"]]
    cart_sum = sum(line_totals) if line_totals else None
    has_on_request = any(not item["line_total"] for item in items)
    return cart_sum, has_on_request


def cart_view(request):
    items = _resolve_cart_items(get_cart(request.session))
    cart_sum, has_on_request = _price_totals(items)
    return render(request, "orders/cart.html", {
        "cart_items": items,
        "cart_sum": cart_sum,
        "has_on_request": has_on_request,
        "form": OrderForm(),
    })


def _render_cart_rows(items):
    """Render all cart item rows for HTMX swap."""
    return "".join(
        render_to_string("orders/_cart_item.html", {"item": item})
        for item in items
    )


def _cart_count_html(count):
    """Render cart count badge for OOB swap."""
    return render_to_string("orders/_cart_count.html", {"count": count, "oob": True})


def _cart_rows_response(cart_data):
    """Rows + OOB badge + OOB cart sum, swaps into #cart-items."""
    items = _resolve_cart_items(cart_data)
    cart_sum, has_on_request = _price_totals(items)
    total_html = render_to_string("orders/_cart_sum.html", {
        "cart_sum": cart_sum,
        "has_on_request": has_on_request,
        "oob": True,
    })
    return HttpResponse(
        _render_cart_rows(items)
        + _cart_count_html(cart_total(cart_data))
        + total_html
    )


@require_POST
def cart_add(request):
    product_id = parse_int(request.POST.get("product_id"), 0)
    packaging_id = parse_int(request.POST.get("packaging_id"), 0) or None
    quantity = parse_quantity(request.POST.get("quantity", 1))

    if not Product.objects.filter(pk=product_id).exists():
        return HttpResponse(status=400)
    if packaging_id and not Packaging.objects.filter(
        pk=packaging_id, product_id=product_id
    ).exists():
        return HttpResponse(status=400)

    key = str(product_id)
    cart_data = get_cart(request.session)

    if key in cart_data:
        cart_data[key]["quantity"] = min(
            cart_data[key]["quantity"] + quantity, CART_MAX_QUANTITY
        )
        if packaging_id is not None:
            cart_data[key]["packaging_id"] = packaging_id
    else:
        cart_data[key] = {
            "packaging_id": packaging_id,
            "quantity": quantity,
        }

    save_cart(request.session, cart_data)
    return HttpResponse(str(cart_total(cart_data)))


@require_POST
def cart_increase(request, product_id):
    cart_data = get_cart(request.session)
    key = str(product_id)

    if key not in cart_data:
        return HttpResponse(status=404)

    cart_data[key]["quantity"] = min(
        cart_data[key]["quantity"] + 1, CART_MAX_QUANTITY
    )
    save_cart(request.session, cart_data)
    return _cart_rows_response(cart_data)


@require_POST
def cart_decrease(request, product_id):
    cart_data = get_cart(request.session)
    key = str(product_id)

    if key not in cart_data:
        return HttpResponse(status=404)

    cart_data[key]["quantity"] -= 1
    if cart_data[key]["quantity"] <= 0:
        del cart_data[key]
    save_cart(request.session, cart_data)
    return _cart_rows_response(cart_data)


@require_POST
def cart_remove(request, product_id):
    cart_data = get_cart(request.session)
    key = str(product_id)

    if key not in cart_data:
        return HttpResponse(status=404)

    del cart_data[key]
    save_cart(request.session, cart_data)
    return _cart_rows_response(cart_data)


@require_POST
def order_create(request):
    cart_data = get_cart(request.session)

    if not cart_data:
        return redirect("orders:cart")

    items = _resolve_cart_items(cart_data)
    cart_sum, has_on_request = _price_totals(items)

    form = OrderForm(request.POST)
    if not form.is_valid():
        return render(request, "orders/cart.html", {
            "cart_items": items,
            "cart_sum": cart_sum,
            "has_on_request": has_on_request,
            "form": form,
        })

    if not items:
        messages.warning(
            request,
            "Товары из вашей корзины больше не доступны. Обновите корзину.",
        )
        save_cart(request.session, {})
        return redirect("orders:cart")

    with transaction.atomic():
        order = form.save()
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                packaging=item["packaging"],
                quantity=item["quantity"],
            )
        save_cart(request.session, {})

    logger.info(
        "New order #%d created",
        order.pk,
    )

    return redirect("orders:order_success")


def order_success(request):
    return render(request, "orders/order_success.html")
