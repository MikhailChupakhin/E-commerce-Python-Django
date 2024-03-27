import json
import os

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from api.serializers.orders_serializers import DeliveryMethodSerializer
from api.serializers.products_serializers import ProductSerializer
from api.serializers.users_serializers import UserLoginSerializer, UserRegistrationSerializer, UserSerializer, \
    UserProfileFormSerializer, UserCartSerializer, CallbackQuerySerializer, SubscriptionSerializer
from api.utils.breadcrumbs import get_breadcrumbs
from api.utils.misc import gt_check_get_cached_basket
from api.views.products_views import BaseAPIView
from orders.models import DeliveryMethod
from products.models import Basket, Product
from users.forms import UserLoginForm
from users.forms import UserRegistrationForm
from users.models import EmailVerification, User, CallbackQuery, Subscription, PromoCode
from users.utils import recalculate_total_price, recalculate_total_price_guest, get_updated_cart_data_guest
from orders.tasks import send_notification_on_create
from api.utils.exception_handler import custom_exception_handler


class UserLoginAPIView(APIView):
    # {
    #     "username": "AdminDB",
    #     "password": "Perpetuum1"
    # }
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        form = UserLoginForm()
        form_data = {
            'username': {
                'value': form['username'].value(),
                'placeholder': form.fields['username'].widget.attrs.get('placeholder', ''),
            },
            'password': {
                'value': form['password'].value(),
                'placeholder': form.fields['password'].widget.attrs.get('placeholder', ''),
            },
        }
        return Response({'form': form_data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({'detail': '1', 'sk': f'{request.session.session_key}'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': '0'}, status=status.HTTP_401_UNAUTHORIZED)


class UserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        form = UserRegistrationForm()
        form_data = {
            'first_name': {
                'value': form['first_name'].value(),
                'placeholder': form.fields['first_name'].widget.attrs.get('placeholder', ''),
            },
            'last_name': {
                'value': form['last_name'].value(),
                'placeholder': form.fields['last_name'].widget.attrs.get('placeholder', ''),
            },
            'username': {
                'value': form['username'].value(),
                'placeholder': form.fields['username'].widget.attrs.get('placeholder', ''),
            },
            'email': {
                'value': form['email'].value(),
                'placeholder': form.fields['email'].widget.attrs.get('placeholder', ''),
            },
            'password1': {
                'value': form['password1'].value(),
                'placeholder': form.fields['password1'].widget.attrs.get('placeholder', ''),
            },
            'password2': {
                'value': form['password2'].value(),
                'placeholder': form.fields['password2'].widget.attrs.get('placeholder', ''),
            },
        }
        return Response({'form': form_data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_data = {
            'first_name': serializer.validated_data['first_name'],
            'last_name': serializer.validated_data['last_name'],
            'username': serializer.validated_data['username'],
            'email': serializer.validated_data['email'],
            'password1': serializer.validated_data['password1'],
            'password2': serializer.validated_data['password2'],
        }

        form = UserRegistrationForm(user_data)

        if form.is_valid():
            form.save()
            return Response({'detail': 'Поздравляем, Вы успешно зарегистрировались!'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': 'Ошибка при регистрации', 'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(BaseAPIView, RetrieveUpdateAPIView):
    serializer_class = UserProfileFormSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        context = {}
        user = self.get_object()
        serializer = self.get_serializer(user)

        context.update(serializer.data)
        return Response(context)

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCartAPIView(BaseAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        context = {}
        seo_data = {
            'title': f'{os.environ.get("BRANDNAME")} - Корзина',
            'meta-description': f'{os.environ.get("BRANDNAME")} - Корзина'
        }

        basket_items = Basket.objects.filter(user=self.request.user)
        print(basket_items)
        total_items = sum(item.quantity for item in basket_items)
        order_total_price = sum(item.product.total_price * item.quantity for item in basket_items)
        delivery_methods = DeliveryMethod.objects.filter(is_active=True)
        delivery_methods_serializer = DeliveryMethodSerializer(delivery_methods, many=True)
        delivery_methods_data = delivery_methods_serializer.data
        selected_delivery_method_id = request.session.get('selected_delivery_method_id')

        serializer = UserCartSerializer({
            'breadcrumbs': [["/", "Главная"], ["/users/cart/", "Корзина"]],
            'seo_data': seo_data,
            'cart_items': basket_items,
            'selected_delivery_method_id': selected_delivery_method_id,
            'products_in_cart': total_items,
            'order_total_price': order_total_price,
            'delivery_methods': delivery_methods_data,
        })

        context.update(serializer.data)

        return Response(context)


class UserCartRemoveAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            user_basket = get_object_or_404(Basket, user=request.user, product_id=request.data.get('product_id'))
            user_basket.delete()
            user_cart_items = Basket.objects.filter(user=request.user)
            order_total_price = recalculate_total_price(user_cart_items)
            response_data = {'success': True, 'order_total_price': order_total_price}
            return Response(response_data)
        except Basket.DoesNotExist:
            return Response({'error': 'Basket item not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("Error:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GuestCartAPIView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        guest_token, _, basket_data = gt_check_get_cached_basket(request)
        if guest_token == None:
            return Response({'message': 'Missing guest_token in request headers.'}, status=status.HTTP_401_UNAUTHORIZED)

        context = {}
        seo_data = {
            'title': f'{os.environ.get("BRANDNAME")} - Корзина',
            'meta-description': f'{os.environ.get("BRANDNAME")} - Корзина'
        }

        cart_items = []
        print(basket_data)
        for item_id, quantity in basket_data.items():
            product = get_object_or_404(Product, id=item_id)

            product_serializer = ProductSerializer(product)
            product_data = product_serializer.data

            cart_items.append({
                'product': product_data,
                'quantity': quantity,
            })

        delivery_methods = DeliveryMethod.objects.filter(is_active=True)
        delivery_methods_serializer = DeliveryMethodSerializer(delivery_methods, many=True)
        delivery_methods_data = delivery_methods_serializer.data
        selected_delivery_method_id = request.session.get('selected_delivery_method_id')
        order_total_price = sum(float(item_data['product']['total_price']) * item_data['quantity'] for item_data in cart_items)

        response_data = {
            'breadcrumbs': [["/", "Главная"], ["/users/cart/", "Корзина"]],
            'seo_data': seo_data,
            'cart_items': cart_items,
            'selected_delivery_method_id': selected_delivery_method_id,
            'delivery_methods': delivery_methods_data,
            'order_total_price': order_total_price,
        }

        context.update(response_data)

        return Response(context, status=status.HTTP_200_OK)


class GuestCartRemoveAPIView(APIView):
    def post(self, request, *args, **kwargs):
        guest_token, redis_connection, basket_data = gt_check_get_cached_basket(request)

        try:
            product_id = request.data.get('product_id')
            if product_id is None:
                return Response({'error': 'Product ID is required in the request body'},
                                status=status.HTTP_400_BAD_REQUEST)

            if str(product_id) in basket_data:
                del basket_data[str(product_id)]
                redis_connection.set(guest_token, json.dumps(basket_data), ex=3600)
                order_total_price = recalculate_total_price_guest(basket_data)
                response_data = {'success': True, 'order_total_price': order_total_price}
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Basket item not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserCartUpdateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            quantity_change_type = request.data.get('operation_type')
            product = get_object_or_404(Product, id=request.data.get('product_id'))

            user_basket = get_object_or_404(Basket, user=request.user, product_id=request.data.get('product_id'))

            if quantity_change_type == 'increase':
                new_quantity = user_basket.quantity + 1
                if new_quantity <= product.quantity:
                    user_basket.quantity = new_quantity
                    user_basket.save()
                    return Response({'message': 'performed', 'upd_qty': new_quantity})
                else:
                    return Response({'error': 'maximal'}, status=status.HTTP_200_OK)
            elif quantity_change_type == 'decrease':
                if user_basket.quantity > 1:
                    user_basket.quantity -= 1
                    user_basket.save()
                    return Response({'message': 'performed', 'upd_qty': user_basket.quantity})
                elif user_basket.quantity == 1:
                    return Response({'error': 'minimal'})
            elif quantity_change_type == 'input':
                input_quantity = request.data.get('input_quantity')
                if input_quantity <= product.quantity:
                    user_basket.quantity = input_quantity
                    user_basket.save()
                    return Response({'message': 'performed', 'upd_qty': input_quantity})
                else:
                    user_basket.quantity = product.quantity
                    user_basket.save()
                    return Response({'message': 'excess', 'upd_qty': product.quantity})
        except Exception as e:
            return Response({'error': f'{e}'}, status=status.HTTP_404_NOT_FOUND)


class GuestCartUpdateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        guest_token, redis_connection, basket_data = gt_check_get_cached_basket(request)
        try:
            product_id = request.data.get('product_id')
            quantity_change_type = request.data.get('operation_type')

            product = get_object_or_404(Product, id=product_id)
            product_id = str(product_id)
            if product_id in basket_data:
                if quantity_change_type == 'increase':
                    new_quantity = basket_data[product_id] + 1
                    if new_quantity <= product.quantity:
                        basket_data[product_id] = new_quantity
                        redis_connection.set(guest_token, json.dumps(basket_data), ex=3600)
                        return Response({'message': 'performed', 'upd_qty': new_quantity})
                    else:
                        return Response({'error': 'maximal'}, status=status.HTTP_200_OK)
                elif quantity_change_type == 'decrease':
                    if basket_data[product_id] > 1:
                        basket_data[product_id] -= 1
                        redis_connection.set(guest_token, json.dumps(basket_data), ex=3600)
                        return Response({'message': 'performed', 'upd_qty': basket_data[product_id]})
                    elif basket_data[product_id] == 1:
                        return Response({'error': 'minimal'})
                elif quantity_change_type == 'input':
                    print('INPUT')
                    return Response({'error': 'доделать input'})
            else:
                print('product_id not in basket_data...')
                return Response({'error': f'product_id not in basket_data'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'{e}'}, status=status.HTTP_404_NOT_FOUND)


class SaveDeliveryAUTHUserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        delivery_method_id = request.data.get('deliveryMethodId')
        redis_connection = get_redis_connection("default")
        cache_key = f'user_{request.user.id}_del_method'
        redis_connection.set(cache_key, delivery_method_id, ex=3600)
        return Response({'message': 'Данные о доставке сохранены.'}, status=status.HTTP_200_OK)


class SaveDeliveryNOAUTHUserAPIView(APIView):
    def post(self, request, *args, **kwargs):
        delivery_method_id = request.data.get('deliveryMethodId')
        redis_connection = get_redis_connection("default")
        guest_token = request.headers.get('guest-token')
        cache_key = f'guest_{guest_token}_del_method'
        redis_connection.set(cache_key, delivery_method_id, ex=3600)
        return Response({'message': 'Данные о доставке сохранены.'}, status=status.HTTP_200_OK)


class EmailVerificationAPIView(APIView):
    def get(self, request, *args, **kwargs):
        code = kwargs.get('code')
        email = kwargs.get('email')

        if not code or not email:
            raise NotFound(detail='Code and email are required in the URL.')

        user = get_object_or_404(User, email=email)
        email_verifications = EmailVerification.objects.filter(user=user, code=code)

        if email_verifications.exists() and not email_verifications.first().is_expired():
            user.is_verified_email = True
            user.save()
            return Response({'message': 'Адрес электронной почты успешно подтвержден'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Неверный или устаревший код верификации.'}, status=status.HTTP_400_BAD_REQUEST)


class CreateCallbackQueryAPIView(APIView):
    def post(self, request, format=None):
        post_data = json.loads(request.body.decode("utf-8"))
        name = post_data.get('name')
        phone = post_data.get('phone')
        data = {'name': name, 'phone': phone}

        serializer = CallbackQuerySerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({'success': True}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@receiver(post_save, sender=CallbackQuery)
def send_callbackquery_notification(sender, instance, created, **kwargs):
    if created:
        message_text = f"\U0001F4DEНужен обратный звонок!\U0001F4DE ID: {instance.id} Дата: {instance.created_at.strftime('%Y-%m-%d %H:%M')} Имя: {instance.name} Телефон: {instance.phone}"
        send_notification_on_create.apply_async(args=[message_text])


class SubscribeNewsAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")

        if email:
            subscription = Subscription(email=email)
            subscription.save()

            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)


class ApplyPromoCodeAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        promo_code = request.data.get('promo_code')

        try:
            promo = PromoCode.objects.get(
                code=promo_code,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now(),
            )

            if promo.current_uses >= promo.max_uses:
                return Response({'error': 'Промо-код использован максимальное количество раз'}, status=status.HTTP_400_BAD_REQUEST)

        except PromoCode.DoesNotExist:
            return Response({'error': 'Промо-код не найден или не активен'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.promo_code = promo
        request.user.save()

        return Response({'success': True, 'message': 'Промо-код успешно применен.'}, status=status.HTTP_200_OK)