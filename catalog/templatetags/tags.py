from django import template
from contextlib import suppress
from more_itertools import first
from catalog.models import Product
from prices.models import Price


register = template.Library()


@register.filter
def get_current_price(prices, product):
    with suppress(Price.DoesNotExist):
        return prices.get(product=product)
    return 0


@register.filter
def get_ident(filter, pref):
    return filter['ident'].replace(f'{pref}_', '')


@register.filter
def get_cart_item(cart, product):
    return first(cart.to_json(str(product.id)),{})


@register.filter
def decimal_price(price):
    return price.replace(',','.')
