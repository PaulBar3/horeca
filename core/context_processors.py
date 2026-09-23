from django.conf import settings


def site_context(request):
    cart = request.session.get(settings.CART_SESSION_KEY, {})
    return {
        "site_name": "FOODCORE",
        "site_tagline": "Основа вашего меню",
        "cart_count": sum(item["quantity"] for item in cart.values()),
    }
