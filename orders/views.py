import logging

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
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
    return max(1, _parse_int(value, default))


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
        items.append({
            "product": product,
            "packaging": packaging or product.packagings.first(),
            "quantity": item_data.get("quantity", 1),
        })
    return items


def cart_view(request):
    items = _resolve_cart_items(_get_cart(request.session))
    return render(request, "orders/cart.html", {"cart_items": items})


@require_POST
def cart_add(request):
    product_id = request.POST.get("product_id")
    packaging_id = request.POST.get("packaging_id")
    quantity = _parse_quantity(request.POST.get("quantity", 1))

    cart_data = _get_cart(request.session)

    if product_id in cart_data:
        cart_data[product_id]["quantity"] += quantity
    else:
        cart_data[product_id] = {
            "packaging_id": packaging_id,
            "quantity": quantity,
        }

    _save_cart(request.session, cart_data)

    count = _cart_total(cart_data)
    return HttpResponse(
        f'<span id="cart-count" class="absolute -top-2 -right-3 '
        f'bg-orange-500 text-xs rounded-full w-5 h-5 flex items-center '
        f'justify-center">{count}</span>'
    )


@require_POST
def cart_update(request, product_id):
    delta = _parse_int(request.POST.get("delta", 0))
    cart_data = _get_cart(request.session)
    key = str(product_id)

    if key not in cart_data:
        return HttpResponse(status=404)

    cart_data[key]["quantity"] += delta
    if cart_data[key]["quantity"] <= 0:
        del cart_data[key]
        html = ""
    else:
        html = str(cart_data[key]["quantity"])

    _save_cart(request.session, cart_data)

    count = _cart_total(cart_data)
    return HttpResponse(
        f'{html}'
        f'<span id="cart-count" hx-swap-oob="true" class="absolute '
        f'-top-2 -right-3 bg-orange-500 text-xs rounded-full w-5 h-5 '
        f'flex items-center justify-center">{count}</span>'
    )


@require_POST
def cart_remove(request, product_id):
    cart_data = _get_cart(request.session)
    key = str(product_id)

    if key not in cart_data:
        return HttpResponse(status=404)

    del cart_data[key]
    _save_cart(request.session, cart_data)

    count = _cart_total(cart_data)
    return HttpResponse(
        f'<span id="cart-count" hx-swap-oob="true" class="absolute '
        f'-top-2 -right-3 bg-orange-500 text-xs rounded-full w-5 h-5 '
        f'flex items-center justify-center">{count}</span>'
    )


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
        return render(request, "orders/cart.html", {
            "cart_items": items,
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
        "New order #%d from %s (%s)",
        order.pk, order.contact_name, order.company,
    )

    return redirect("orders:order_success")


def order_success(request):
    return render(request, "orders/order_success.html")
