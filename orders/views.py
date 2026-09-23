import logging

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from catalog.models import Packaging, Product

from .forms import OrderForm
from .models import OrderItem

logger = logging.getLogger(__name__)


def _get_cart(session):
    return session.get(settings.CART_SESSION_KEY, {})


def _save_cart(session, cart_data):
    session[settings.CART_SESSION_KEY] = cart_data
    session.modified = True


def _cart_total(cart_data):
    return sum(item["quantity"] for item in cart_data.values())


def _parse_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_quantity(value, default=1):
    return max(1, min(9999, _parse_int(value, default)))


def _resolve_cart_items(cart_data):
    items = []
    for product_id, item_data in cart_data.items():
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            continue
        packaging = None
        if item_data.get("packaging_id"):
            try:
                packaging = Packaging.objects.get(
                    pk=item_data["packaging_id"]
                )
            except Packaging.DoesNotExist:
                pass
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
    items = _resolve_cart_items(_get_cart(request.session))
    cart_sum, has_on_request = _price_totals(items)
    return render(request, "orders/cart.html", {
        "cart_items": items,
        "cart_sum": cart_sum,
        "has_on_request": has_on_request,
    })


CART_MAX_QUANTITY = 9999


def _render_cart_rows(items):
    """Render all cart item rows for HTMX swap."""
    return "".join(
        render_to_string("orders/_cart_item.html", {"item": item})
        for item in items
    )


def _cart_count_html(count):
    """Render cart count badge for OOB swap."""
    return (
        f'<span id="cart-count" hx-swap-oob="true" class="absolute '
        f'-top-2 -right-3 bg-orange-500 text-xs rounded-full w-5 h-5 '
        f'flex items-center justify-center">{count}</span>'
    )


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
        + _cart_count_html(_cart_total(cart_data))
        + total_html
    )


@require_POST
def cart_add(request):
    product_id = _parse_int(request.POST.get("product_id"), 0)
    packaging_id = _parse_int(request.POST.get("packaging_id"), 0) or None
    quantity = _parse_quantity(request.POST.get("quantity", 1))

    if not Product.objects.filter(pk=product_id).exists():
        return HttpResponse(status=400)
    if packaging_id and not Packaging.objects.filter(
        pk=packaging_id, product_id=product_id
    ).exists():
        return HttpResponse(status=400)

    key = str(product_id)
    cart_data = _get_cart(request.session)

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

    _save_cart(request.session, cart_data)
    return HttpResponse(str(_cart_total(cart_data)))


@require_POST
def cart_increase(request, product_id):
    cart_data = _get_cart(request.session)
    key = str(product_id)

    if key not in cart_data:
        return HttpResponse(status=404)

    cart_data[key]["quantity"] = min(
        cart_data[key]["quantity"] + 1, CART_MAX_QUANTITY
    )
    _save_cart(request.session, cart_data)
    return _cart_rows_response(cart_data)


@require_POST
def cart_decrease(request, product_id):
    cart_data = _get_cart(request.session)
    key = str(product_id)

    if key not in cart_data:
        return HttpResponse(status=404)

    cart_data[key]["quantity"] -= 1
    if cart_data[key]["quantity"] <= 0:
        del cart_data[key]
    _save_cart(request.session, cart_data)
    return _cart_rows_response(cart_data)


@require_POST
def cart_remove(request, product_id):
    cart_data = _get_cart(request.session)
    key = str(product_id)

    if key not in cart_data:
        return HttpResponse(status=404)

    del cart_data[key]
    _save_cart(request.session, cart_data)
    return _cart_rows_response(cart_data)


def cart_count(request):
    return render(request, "orders/cart_count.html", {
        "count": _cart_total(_get_cart(request.session)),
    })


@require_POST
def order_create(request):
    cart_data = _get_cart(request.session)

    if not cart_data:
        return redirect("orders:cart")

    form = OrderForm(request.POST)
    if not form.is_valid():
        items = _resolve_cart_items(cart_data)
        cart_sum, has_on_request = _price_totals(items)
        return render(request, "orders/cart.html", {
            "cart_items": items,
            "cart_sum": cart_sum,
            "has_on_request": has_on_request,
            "form": form,
        })

    order = form.save()

    for item in _resolve_cart_items(cart_data):
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            packaging=item["packaging"],
            quantity=item["quantity"],
        )

    _save_cart(request.session, {})

    logger.info(
        "New order #%d created",
        order.pk,
    )

    return redirect("orders:order_success")


def order_success(request):
    return render(request, "orders/order_success.html")
