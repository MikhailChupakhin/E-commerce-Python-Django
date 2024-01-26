from rest_framework import serializers

from orders.constants import PROVINCE_CHOICES
from orders.models import DeliveryMethod, PaymentMethod, Order, OrderItem, BuyInOneClick


class DeliveryMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryMethod
        fields = '__all__'


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class BuyInOneClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyInOneClick
        fields = '__all__'


class OrderFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'email', 'city', 'province', 'address', 'phone', 'aux_phone', 'company', 'zipcode', 'payment_method', 'delivery_method')


