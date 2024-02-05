from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from products.models import Basket, Product
from users.models import User, PromoCode

from .constants import PROVINCE_CHOICES


class DeliveryMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Метод доставки'
        verbose_name_plural = 'Методы доставки'

    def __str__(self):
        return f'DelMethod #{self.id}. {self.name}'


class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Метод оплаты'
        verbose_name_plural = 'Методы оплаты'

    def __str__(self):
        return f'{self.name}'


class Order(models.Model):
    CREATED = 0
    PAID = 1
    ON_WAY = 2
    DELIVERED = 3
    CANCELED = 4
    STATUSES = (
        (CREATED, 'Создан'),
        (PAID, 'Оплачен'),
        (ON_WAY, 'В пути'),
        (DELIVERED, 'Доставлен'),
        (CANCELED, 'Отменен'),
    )

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=256)
    city = models.CharField(max_length=50)
    province = models.CharField(choices=PROVINCE_CHOICES)
    address = models.CharField(max_length=256)
    phone = models.CharField(max_length=20)
    aux_phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=64, blank=True)
    zipcode = models.CharField(max_length=6, blank=True)
    items = models.ManyToManyField(Product, through='OrderItem', related_name='orders')
    created = models.DateTimeField(auto_now_add=True)
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    status = models.PositiveSmallIntegerField(default=CREATED, choices=STATUSES)
    tech_comment = models.CharField(max_length=256, blank=True, null=True)
    total_sum = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.PROTECT, default=1)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, default=1)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Order #{self.id}. {self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        try:
            order_items = self.order_items.all()
            products_total = sum(item.product.total_price * item.quantity for item in order_items)

            delivery_price = self.delivery_method.price

            self.total_sum = products_total + delivery_price
        except Exception as e:
            self.total_sum = 0

        super().save(*args, **kwargs)

    # Расчет суммы заказа с уч. скидок и промо-кода
    def finally_sum(self):
        order_items = OrderItem.objects.filter(order=self)

        finally_sum = sum(order_item.price_at_order for order_item in order_items)

        if self.promo_code:
            finally_sum -= self.promo_code.discount

        return finally_sum

    def purchased_items(self):
        return OrderItem.objects.filter(order=self)

    def update_after_payment(self):
        self.status = self.PAID
        self.save()

    def apply_promo_code(self, promo_code):
        if promo_code:
            discount = promo_code.discount
            if discount:
                self.total_sum -= discount
                promo_code.current_uses += 1
                promo_code.save()
                self.promo_code = promo_code
                self.save()

    def update_after_order(self):
        baskets = Basket.objects.filter(user=self.initiator)
        unavailable_products = []

        for basket in baskets:
            product = basket.product
            if product.quantity >= basket.quantity:
                order_item = OrderItem(
                    order=self,
                    product=product,
                    quantity=basket.quantity,
                    price_at_order=product.price
                )
                order_item.save()
            else:
                unavailable_quantity = basket.quantity - product.quantity
                unavailable_products.append((product, unavailable_quantity))

                order_item = OrderItem(
                    order=self,
                    product=product,
                    quantity=product.quantity,
                    price_at_order=product.price
                )
                order_item.save()

        if unavailable_products:
            unavailable_info = ", ".join(
                [f"{product.name} ({quantity} шт.)" for product, quantity in unavailable_products])
            self.tech_comment = f"Недоступные товары: {unavailable_info}"

        self.save()

        baskets.delete()

    def update_after_order_noauth(self, basket_data):
        unavailable_products = []

        for product_id, quantity in basket_data.items():
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                continue

            if product.quantity >= quantity:
                order_item = OrderItem(
                    order=self,
                    product=product,
                    quantity=quantity,
                    price_at_order=product.price
                )
                order_item.save()
            else:
                unavailable_quantity = quantity - product.quantity
                unavailable_products.append((product, unavailable_quantity))

                order_item = OrderItem(
                    order=self,
                    product=product,
                    quantity=product.quantity,
                    price_at_order=product.price
                )
                order_item.save()

        if unavailable_products:
            unavailable_info = ", ".join(
                [f"{product.name} ({quantity} шт.)" for product, quantity in unavailable_products])
            self.tech_comment = f"Недоступные товары: {unavailable_info}"

        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.product} (Количество: {self.quantity})'

    _previous_quantity = None

    def save(self, *args, **kwargs):
        self.product_name = self.product.name
        if self.pk:
            current_order_item = OrderItem.objects.get(pk=self.pk)
            self._previous_quantity = current_order_item.quantity
        else:
            self._previous_quantity = 0

        super(OrderItem, self).save(*args, **kwargs)


@receiver(post_save, sender=OrderItem)
def update_product_quantity(sender, instance, **kwargs):
    product = instance.product
    quantity_change = instance.quantity - instance._previous_quantity

    product.quantity -= quantity_change
    product.save()


class BuyInOneClick(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка на покупку в один клик'
        verbose_name_plural = 'Заявки на покупку в один клик'

    def __str__(self):
        return f'Заявка {self.pk} на товар "{self.product}"'

