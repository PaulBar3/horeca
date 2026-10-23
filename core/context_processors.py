from orders.cart import cart_total, get_cart


def site_context(request):
    return {
        "cart_count": cart_total(get_cart(request.session)),
    }
