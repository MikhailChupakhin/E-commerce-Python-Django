from django.db.models.signals import post_save
from django.dispatch import receiver
from django_redis import get_redis_connection
from rest_framework.generics import RetrieveAPIView, ListAPIView

from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework import status

from django.core.exceptions import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication

from orders.tasks import send_notification_on_create

from orders.constants import PROVINCE_CHOICES

from orders.models import DeliveryMethod, Order
import logging

from users.utils import clear_user_session
from .products_views import BaseAPIView
from ..serializers.orders_serializers import OrderSerializer, OrderFormSerializer
from ..utils.misc import gt_check_get_cached_basket

logger = logging.getLogger(__name__)


class CheckoutAUTHAPIView(BaseAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        context = {}
        base_response = super().get(request, *args, **kwargs)
        redis_connection = get_redis_connection("default")
        cache_key = f'user_{request.user.id}_del_method'
        selected_delivery_method_id = redis_connection.get(cache_key)

        try:
            selected_delivery_method = DeliveryMethod.objects.get(id=selected_delivery_method_id)
        except Exception as e:
            return Response({"error": "Неверный метод доставки."}, status=500)

        order_instance = Order()
        form_data = {
            'first_name': '',
            'last_name': '',
            'email': '',
            'city': '',
            'province': '',
            'address': '',
            'phone': '',
            'aux_phone': '',
            'company': '',
            'zipcode': '',
            'payment_method': None,
            'delivery_method': selected_delivery_method_id,
        }
        serializer = OrderFormSerializer(order_instance, data=form_data)
        serializer.is_valid()

        response_data = {
            'PROVINCE_CHOICES': PROVINCE_CHOICES,
            'selected_delivery_method_id': selected_delivery_method_id,
            'selected_delivery_price': selected_delivery_method.price,
            'selected_delivery_name': selected_delivery_method.name,
            'form': serializer.data,
        }
        context['base_data'] = base_response.data
        context.update(response_data)

        return Response(context, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = OrderFormSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            order = Order.objects.create(**serializer.validated_data)

            order.initiator = request.user

            if request.user.promo_code:
                order.apply_promo_code(request.user.promo_code)
                request.user.promo_code = None
                request.user.save()

            order.save()
            payment_method = serializer.validated_data.get('payment_method')

            if payment_method.id == 1:
                order.update_after_order()

                return Response({"message": "Заказ успешно оформлен"}, status=201)
            else:
                return Response({"error": "Неверный метод оплаты"}, status=400)
        except ValidationError as e:
            errors = serializer.errors
            return Response({"error": "Ошибка валидации формы", "details": errors}, status=400)
        except Exception as e:
            return Response({"error": "Внутренняя ошибка сервера"}, status=500)


class CheckoutNOAUTHAPIView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        context = {}
        base_response = super().get(request, *args, **kwargs)
        redis_connection = get_redis_connection("default")
        cache_key = f'user_{request.user.id}_del_method'
        selected_delivery_method_id = redis_connection.get(cache_key)

        try:
            selected_delivery_method = DeliveryMethod.objects.get(id=selected_delivery_method_id)
        except Exception as e:
            return Response({"error": "Неверный метод доставки."}, status=500)

        order_instance = Order()
        form_data = {
            'first_name': '',
            'last_name': '',
            'email': '',
            'city': '',
            'province': '',
            'address': '',
            'phone': '',
            'aux_phone': '',
            'company': '',
            'zipcode': '',
            'payment_method': None,
            'delivery_method': selected_delivery_method_id,
        }
        serializer = OrderFormSerializer(order_instance, data=form_data)
        serializer.is_valid()

        response_data = {
            'PROVINCE_CHOICES': PROVINCE_CHOICES,
            'selected_delivery_method_id': selected_delivery_method_id,
            'selected_delivery_price': selected_delivery_method.price,
            'selected_delivery_name': selected_delivery_method.name,
            'form': serializer.data,
        }
        context['base_data'] = base_response.data
        context.update(response_data)

        return Response(context, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = OrderFormSerializer(data=request.data)
        guest_token, redis_connection, basket_data = gt_check_get_cached_basket(request)

        try:
            serializer.is_valid(raise_exception=True)
            order = Order.objects.create(**serializer.validated_data)
            order.save()
            payment_method = serializer.validated_data.get('payment_method')

            if payment_method.id == 1:
                order.update_after_order_noauth(basket_data)
                redis_connection.delete(guest_token)

                return Response({"message": "Заказ успешно оформлен"}, status=201)
            else:
                return Response({"error": "Неверный метод оплаты"}, status=400)
        except ValidationError as e:
            errors = serializer.errors
            return Response({"error": "Ошибка валидации формы", "details": errors}, status=400)
        except Exception as e:
            return Response({"error": "Внутренняя ошибка сервера"}, status=500)


@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    if created:
        message_text = f"Новый заказ! ID заказа: {instance.id} Дата создания: {instance.created.strftime('%Y-%m-%d %H:%M')} Email: {instance.email}"
        send_notification_on_create.apply_async(args=[message_text])


class OrderDetailAPIView(BaseAPIView, RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        try:
            order = Order.objects.get(id=order_id)
            if order.initiator != self.request.user:
                return Response({"detail": "Вы не имеете доступа к данному заказу."}, status=status.HTTP_403_FORBIDDEN)
            context = {}
            base_response = super().get(request, *args, **kwargs)
            serializer = self.get_serializer(order)
            context['base_data'] = base_response.data
            context.update(serializer.data, status=status.HTTP_200_OK)
            return Response(context)
        except Order.DoesNotExist:
            return Response({"detail": "Заказ не найден."}, status=status.HTTP_404_NOT_FOUND)


class OrderListAPIView(BaseAPIView, ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs):
        context = {}
        base_response = super().get(request, *args, **kwargs)
        serializer = self.get_serializer(self.get_queryset(), many=True)
        context['base_data'] = base_response.data
        context['orders'] = serializer.data
        return Response(context, status=status.HTTP_200_OK)

    def get_queryset(self):
        return Order.objects.filter(initiator=self.request.user)