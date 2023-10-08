from django.contrib import admin

from .models import (BuyInOneClick, DeliveryMethod, Order, OrderItem,
                     PaymentMethod)


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'price', 'id']
    fields = (
        'id', 'name',
        'price',
        'is_active',
        'description',
    )
    readonly_fields = ['id']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'id']
    fields = (
        'id', 'name',
        'is_active',
        'description',
    )
    readonly_fields = ['id']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ('product',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['created', 'status', 'tech_comment', 'promo_code', 'get_total_sum', 'first_name', 'phone', 'address']
    fields = (
        'id', 'created', 'promo_code',
        'payment_method', 'delivery_method',
        ('first_name', 'last_name'),
        'email', ('address', 'phone'),
        'status', 'initiator',
    )
    readonly_fields = ['id', 'created']
    inlines = [OrderItemInline]

    def get_total_sum(self, obj):
        return obj.finally_sum()

    get_total_sum.short_description = 'Finaly Sum'


@admin.register(BuyInOneClick)
class BuyInOneClickAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'product', 'created')
    list_filter = ('created',)
    search_fields = ('name', 'phone', 'email', 'product__name')


