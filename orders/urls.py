from django.urls import path

from .views import (CancelTemplateView, CheckInventoryView, CheckoutView,
                    OrderDetailView, OrderListView, SuccessTemplateView)

app_name = 'orders'


urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('<int:pk>/', OrderListView.as_view(), name='orders_list'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order'),
    path('order-success/', SuccessTemplateView.as_view(), name='order_success'),
    path('order-canceled/', CancelTemplateView.as_view(), name='order_canceled'),
    path('check_inventory/', CheckInventoryView.as_view(), name='check_inventory'),
]
