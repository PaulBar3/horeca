"""Cart session helpers shared by views and context processors."""

from django.conf import settings

CART_MAX_QUANTITY = 9999


def get_cart(session):
    return session.get(settings.CART_SESSION_KEY, {})


def save_cart(session, cart_data):
    session[settings.CART_SESSION_KEY] = cart_data
    session.modified = True


def cart_total(cart_data):
    return sum(item["quantity"] for item in cart_data.values())


def parse_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_quantity(value, default=1):
    return max(1, min(CART_MAX_QUANTITY, parse_int(value, default)))
