from django import template
from decimal import Decimal
register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def add_values(value, arg):
    return value + arg

@register.simple_tag
def calculate_total(baskets_total_sum, selected_delivery_price, promo_code_discount):
    # Преобразование в decimal.Decimal, если необходимо
    baskets_total_sum = Decimal(baskets_total_sum)
    selected_delivery_price = Decimal(selected_delivery_price)
    promo_code_discount = Decimal(promo_code_discount) if promo_code_discount else Decimal(0)

    total_before_discount = baskets_total_sum + selected_delivery_price
    total_after_discount = total_before_discount - promo_code_discount
    return total_after_discount

@register.filter(name='comma_to_dot')
def comma_to_dot(value):
    return value.replace(',', '.')


@register.filter
def star_rating(value):
    try:
        num_stars = float(value)
        integer_part = int(num_stars)
        decimal_part = num_stars - integer_part
        stars = '★' * integer_part

        if decimal_part > 0:
            stars += '☆'

        return stars
    except (TypeError, ValueError):
        return ''


@register.filter
def filter_by_name(queryset, name):
    return queryset.filter(name=name)
