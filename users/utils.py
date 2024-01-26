from django.shortcuts import get_object_or_404

from products.models import Product


def recalculate_total_price(cart_items):
    order_total_price = 0

    for cart_item in cart_items:
        order_total_price += cart_item.product.total_price * cart_item.quantity

    return order_total_price


def recalculate_total_price_guest(baskets):
    order_total_price = 0

    for item_id, item_data in baskets.items():
        product = Product.objects.get(id=int(item_id))
        order_total_price += product.total_price * item_data['quantity']

    return order_total_price

def get_updated_cart_data(baskets):
    updated_cart = {
        'cart_items': []
    }
    for basket in baskets:
        product = basket.product
        updated_cart['cart_items'].append({
            'product_id': product.id,
            'product_name': product.name,
            'quantity': basket.quantity,
            'price': product.total_price,
        })
    return updated_cart

def get_updated_cart_data_guest(baskets):
    updated_cart = {
        'cart_items': []
    }
    for product_id, item_data in baskets.items():
        product = get_object_or_404(Product, id=product_id)
        updated_cart['cart_items'].append({
            'product_id': product.id,
            'product_name': product.name,
            'quantity': item_data['quantity'],
            'price': product.total_price,
        })
    return updated_cart

def clear_user_session(session):
    session.clear()




