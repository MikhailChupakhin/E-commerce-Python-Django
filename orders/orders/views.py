from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import (Http404, HttpResponseRedirect, JsonResponse, HttpResponse)
from django.urls import reverse, reverse_lazy
from django.core.exceptions import ValidationError
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from common.views import TitleMixin
from orders.models import DeliveryMethod, Order
from products.models import Basket
from users.utils import clear_user_session
import logging

from .constants import PROVINCE_CHOICES
from .forms import OrderForm
from .tasks import send_notification_on_create

logger = logging.getLogger('main')


class SuccessTemplateView(TitleMixin, TemplateView):
    template_name = 'orders/success.html'
    title = 'IMSOUND - Заказ успешно оформлен!'


class CancelTemplateView(TitleMixin, TemplateView):
    template_name = 'orders/cancel.html'


class OrderListView(TitleMixin, LoginRequiredMixin, ListView):
    template_name = 'orders/orders.html'
    title = 'IMSOUND - Заказы'
    queryset = Order.objects.all()

    def get_queryset(self):
        queryset = super(OrderListView, self).get_queryset()
        return queryset.filter(initiator=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'orders/order.html'
    model = Order

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Проверяем, что текущий пользователь является создателем заказа
        if obj.initiator != self.request.user:
            raise Http404("Вы не имеете доступа к данному заказу.")
        return obj

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context['title'] = f'IMSOUND - Заказ № {self.object.id}'
        return context


class CheckoutView(TitleMixin, CreateView):
    title = 'IMSOUND - Оформление заказа'
    model = Order
    template_name = 'orders/checkout.html'
    form_class = OrderForm
    success_url = reverse_lazy('orders:checkout')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['PROVINCE_CHOICES'] = PROVINCE_CHOICES

        # Получаем значение selected_delivery_price из сессии
        selected_delivery_method_id = self.request.session.get('selected_delivery_method_id')
        context['selected_delivery_method_id'] = selected_delivery_method_id
        context['selected_delivery_price'] = DeliveryMethod.objects.get(id=selected_delivery_method_id).price

        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        try:
            if form.is_valid():

                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.initiator = request.user
                order.save()

                payment_method = form.cleaned_data.get('payment_method')

                # if payment_method == 'card':
                #     baskets = Basket.objects.filter(user=request.user)
                #     checkout_session = stripe.checkout.Session.create(
                #         line_items=baskets.stripe_products(),
                #         metadata={'order_id': order.id},
                #         mode='payment',
                #         success_url='{}{}'.format(settings.DOMAIN_NAME, reverse('orders:order_success')),
                #         cancel_url='{}{}'.format(settings.DOMAIN_NAME, reverse('orders:order_canceled')),
                #     )
                #     order.update_after_order()
                #     return HttpResponseRedirect(checkout_session.url, status=HTTPStatus.SEE_OTHER)
                if payment_method.id == 1: #Наличными при получении
                    if request.user.is_authenticated:
                        order.update_after_order()
                    else:
                        baskets_data = request.session.get('basket', {})
                        order.update_after_order_session(baskets_data)
                        clear_user_session(request.session)

                    return HttpResponseRedirect(reverse('orders:order_success'))
                else:
                    logger.error("Invalid payment method")
        except ValidationError as e:
            logger.error("Form Validation Error:", str(e))
            return self.form_invalid(form)
        except Exception as e:
            logger.error("Error:", str(e))
            return HttpResponse(status=400)

    def get_guest_baskets(self, request):
        baskets_data = request.session.get('basket', {})
        basket_ids = [int(product_id) for product_id in baskets_data.keys()]
        baskets = Basket.objects.filter(id__in=basket_ids)
        return baskets

    def form_valid(self, form):
        # Установка инициатора заказа
        if self.request.user.is_authenticated:
            form.instance.initiator = self.request.user
        else:
            form.instance.initiator = None

        return super().form_valid(form)

@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    if created:
        message_text = f"Новый заказ! ID заказа: {instance.id} Дата создания: {instance.created.strftime('%Y-%m-%d %H:%M')} Email: {instance.email}"
        send_notification_on_create.apply_async(args=[message_text])


class CheckInventoryView(View):
    def post(self, request, *args, **kwargs):
        try:
            baskets = Basket.objects.filter(user=request.user)

            unavailable_products = []
            for basket in baskets:
                product = basket.product
                if basket.quantity > product.quantity:
                    unavailable_products.append({
                        'product_id': product.id,
                        'product_name': product.name,
                        'basket_quantity': basket.quantity,
                        'available_quantity': product.quantity
                    })

            response = {
                'unavailable_products': unavailable_products
            }

            return JsonResponse(response)

        except Exception as e:
            logger.error("Error:", str(e))
            return JsonResponse({'error_message': str(e)})