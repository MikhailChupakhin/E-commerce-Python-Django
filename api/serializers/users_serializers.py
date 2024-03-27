from rest_framework import serializers

from api.serializers.orders_serializers import DeliveryMethodSerializer
from api.serializers.products_serializers import BasketSerializer, ProductSerializer
from users.models import PromoCode, User, EmailVerification, Feedback, CallbackQuery, Subscription


class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)


class UserProfileFormSerializer(serializers.ModelSerializer):
    is_verified_email = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'image', 'username', 'email', 'is_verified_email', 'date_joined')

    def __init__(self, instance=None, *args, **kwargs):
        super(UserProfileFormSerializer, self).__init__(instance=instance, *args, **kwargs)
        for field_name in ['username', 'email', 'date_joined']:
            self.fields[field_name].read_only = True


class UserCartSerializer(serializers.Serializer):
    cart_items = BasketSerializer(many=True)
    selected_delivery_method_id = serializers.IntegerField()
    order_total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    delivery_methods = DeliveryMethodSerializer(many=True)


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


class CallbackQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = CallbackQuery
        fields = ('name', 'phone')


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
