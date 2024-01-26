import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.views import TitleMixin
from orders.models import DeliveryMethod
from orders.tasks import send_notification_on_create
from products.models import Basket, Product
from users.forms import (FeedbackForm, UserLoginForm, UserProfileForm,
                         UserRegistrationForm)
from users.models import CallbackQuery, EmailVerification, User, PromoCode

from .models import Subscription
from .utils import (get_updated_cart_data, get_updated_cart_data_guest,
                    recalculate_total_price, recalculate_total_price_guest)


class UserLoginView(TitleMixin, LoginView):
    template_name = 'users/login.html'
    form_class = UserLoginForm
    title = 'IMSOUND - Авторизация'


class UserRigistrationView(TitleMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/registration.html'
    success_url = reverse_lazy('users:login')
    success_message = 'Поздравляем, Вы успешно зарегистрировались!'
    title = 'IMSOUND - Регистрация'


class UserProfileView(TitleMixin, LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    title = 'IMSOUND - Личный кабинет'

    def get_success_url(self):
        return reverse_lazy('users:profile', args=(self.request.user.pk,))

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_verified_email:
            # Пользователь не подтвердил регистрацию
            messages.warning(self.request,
                             'Ccылка для подтверждения регистрации была отправлена на указанный Вами электронный почтовый адрес! Пожалуйста, закончите регистрацию, перейдя по ссылке в письме.')
            # return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())
        return super().dispatch(request, *args, **kwargs)


class UserCartView(TitleMixin, LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/cart.html'
    title = 'IMSOUND - Корзина'

    def get(self, request, *args, **kwargs):
        basket_items = Basket.objects.filter(user=self.request.user)
        total_items = sum(item.quantity for item in basket_items)
        order_total_price = sum(item.product.total_price * item.quantity for item in basket_items)
        delivery_methods = DeliveryMethod.objects.filter(is_active=True)
        context = {
            'cart_items': basket_items,
            'title': self.title,
            'products_in_cart': total_items,
            'order_total_price': order_total_price,
            'delivery_methods': delivery_methods,
        }

        return render(request, self.template_name, context)


class UserCartRemoveView(View):
    def post(self, request, pk, *args, **kwargs):
        post_data = json.loads(request.body.decode("utf-8"))
        try:
            user_basket = get_object_or_404(Basket, user=request.user, product_id=post_data.get('product_id'))
            user_basket.delete()
            user_cart_items = Basket.objects.filter(user=request.user)
            order_total_price = recalculate_total_price(user_cart_items)
            response_data = {'success': True, 'order_total_price': order_total_price}
            return JsonResponse(response_data)
        except Basket.DoesNotExist:
            return JsonResponse({'error': 'Basket item not found'}, status=404)
        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({'error': str(e)}, status=500)


class UserCartUpdateView(View):
    def post(self, request, *args, **kwargs):
        post_data = json.loads(request.body.decode("utf-8"))
        try:
            product_id = int(post_data.get('product_id'))
            quantity_change_type = post_data.get('quantity_change_type')

            product = get_object_or_404(Product, id=product_id)
            user_basket = get_object_or_404(Basket, user=request.user, product_id=product_id)

            if quantity_change_type == 'increase':
                new_quantity = user_basket.quantity + 1
                if new_quantity <= product.quantity:  # Проверка на доступное количество
                    user_basket.quantity = new_quantity
                else:
                    return JsonResponse({'error': 'Exceeded available quantity for this product'}, status=200)
            elif quantity_change_type == 'decrease':
                if user_basket.quantity > 1:
                    user_basket.quantity -= 1
                else:
                    return JsonResponse({'error': 'Basket item not found'}, status=404)

            user_basket.save()  # Сохранение изменений в корзине

            user_cart_items = Basket.objects.filter(user=request.user)
            order_total_price = recalculate_total_price(user_cart_items)
            updated_cart = get_updated_cart_data(user_cart_items)
            response_data = {'success': True, 'order_total_price': order_total_price, 'updated_cart': updated_cart}
            return JsonResponse(response_data)

        except Exception as e:
            print("Error:", str(e))  # Отладочный вывод
            return JsonResponse({'error': str(e)}, status=500)


class GuestCartView(TitleMixin, View):
    template_name = 'users/cart_guest.html'
    title = 'IMSOUND - Корзина (гость)'

    def get(self, request, *args, **kwargs):
        baskets = request.session.get('basket', {})
        cart_items = []
        for item_id, item_data in baskets.items():
            product = get_object_or_404(Product, id=item_id)

            cart_items.append({
                'product_preview_image': product.image.url,
                'product_id': product.id,
                'product_name': product.name,
                'quantity': item_data['quantity'],
                'price': product.total_price,
            })

        delivery_methods = DeliveryMethod.objects.filter(is_active=True)

        context = {
            'cart_items': cart_items,
            'title': self.title,
            'delivery_methods': delivery_methods,
        }

        order_total_price = sum(item['price'] * item['quantity'] for item in cart_items)
        context['order_total_price'] = order_total_price

        return render(request, self.template_name, context)


class GuestCartRemoveView(View):
    def post(self, request, pk, *args, **kwargs):
        try:
            baskets = request.session.get('basket', {})
            if str(pk) in baskets:
                del baskets[str(pk)]
                request.session['baskets'] = baskets
                order_total_price = recalculate_total_price_guest(baskets)
                response_data = {'success': True, 'order_total_price': order_total_price}
                return JsonResponse(response_data)
            else:
                return JsonResponse({'error': 'Basket item not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class GuestCartUpdateView(View):
    def post(self, request, *args, **kwargs):
        post_data = json.loads(request.body.decode("utf-8"))
        try:
            product_id = post_data.get('product_id')
            quantity_change_type = post_data.get('quantity_change_type')

            product = get_object_or_404(Product, id=product_id)
            baskets = request.session.get('basket', {})
            if str(product_id) in baskets:
                if quantity_change_type == 'increase':
                    new_quantity = baskets[str(product_id)]['quantity'] + 1
                    if new_quantity <= product.quantity:  # Проверка на доступное количество
                        baskets[str(product_id)]['quantity'] = new_quantity
                    else:
                        return JsonResponse({'error': 'Exceeded available quantity for this product'}, status=200)
                elif quantity_change_type == 'decrease':
                    if baskets[str(product_id)]['quantity'] > 1:
                        baskets[str(product_id)]['quantity'] -= 1
                request.session['baskets'] = baskets
                order_total_price = recalculate_total_price_guest(baskets)
                updated_cart = get_updated_cart_data_guest(baskets)
                response_data = {'success': True, 'order_total_price': order_total_price, 'updated_cart': updated_cart}
                return JsonResponse(response_data)
            else:
                return JsonResponse({'error': 'Basket item not found'}, status=404)
        except Exception as e:
            print("Error:", str(e))  # Отладочный вывод
            return JsonResponse({'error': str(e)}, status=500)


class SaveDeliveryToSessionView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        delivery_method_id = data.get('deliveryMethodId')

        # Сохранение данных в сессию
        request.session['selected_delivery_method_id'] = delivery_method_id

        return JsonResponse({'message': 'Данные сохранены в сессии.'})


class EmailVerificationView(TitleMixin, TemplateView):
    title = 'IMSOUND - Подтверждение электронной почты'
    template_name = 'users/email_verification.html'

    def get(self, request, *args, **kwargs):
        code = kwargs['code']
        user = User.objects.get(email=kwargs['email'])
        email_verifications = EmailVerification.objects.filter(user=user, code=code)
        if email_verifications.exists() and not email_verifications.first().is_expired():
            user.is_verified_email = True
            user.save()
            return super(EmailVerificationView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('index'))


class FeedbackView(TitleMixin, TemplateView):
    title = 'IMSOUND - Форма обратной связи'
    template_name = 'users/feedback.html'

    def get(self, request):
        form = FeedbackForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:success_feedback')
        return render(request, self.template_name, {'form': form})


class SuccessFeedbackView(TemplateView):
    template_name = 'users/success_feedback.html'

#### ПЕРЕНЕСЕНО В api/users_views.py
# class CreateCallbackQueryView(APIView):
#     def post(self, request, format=None):
#         post_data = json.loads(request.body.decode("utf-8"))
#         name = post_data.get('name')
#         phone = post_data.get('phone')
#         # Создание словаря с данными для сериализации
#         data = {'name': name, 'phone': phone}
#
#         # Создание экземпляра сериализатора
#         serializer = CallbackQuerySerializer(data=data)
#
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'success': True}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @receiver(post_save, sender=CallbackQuery)
# def send_callbackquery_notification(sender, instance, created, **kwargs):
#     if created:
#         message_text = f"\U0001F4DEНужен обратный звонок!\U0001F4DE ID: {instance.id} Дата: {instance.created_at.strftime('%Y-%m-%d %H:%M')} Имя: {instance.name} Телефон: {instance.phone}"
#         send_notification_on_create.apply_async(args=[message_text])


class SubscribeNewsView(View):
    def post(self, request):
        email = request.POST.get("email")

        if email:
            subscription = Subscription(email=email)
            subscription.save()

            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False})


class ApplyPromoCodeView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        promo_code = data.get('promo_code')
        try:
            promo = PromoCode.objects.get(
                code=promo_code,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now(),
            )

            if promo.current_uses >= promo.max_uses:
                return JsonResponse({'error': 'Промо-код использован максимальное количество раз'})
        except PromoCode.DoesNotExist:
            return JsonResponse({'error': 'Промо-код не найден или не активен'})

        # Уставливаем промо-код для текущего пользователя
        request.user.promo_code = promo
        request.user.save()

        messages.success(request, 'Промо-код успешно применен.')

        return JsonResponse({'success': True, 'discount': promo.discount})