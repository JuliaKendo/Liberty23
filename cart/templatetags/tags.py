from django import template


register = template.Library()


@register.filter
def decimal_price(price):
    return price.replace(',','.')
