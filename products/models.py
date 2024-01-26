import os


from _decimal import ROUND_HALF_UP, Decimal
from ckeditor.fields import RichTextField
from django.contrib.sessions.models import Session
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image
from transliterate import translit

from seo_manager.models import Tag
from users.models import User


class ProductCategory(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = 'Категории'
        verbose_name_plural = 'Категории'

    def save(self, *args, **kwargs):
        if not self.slug:
            transliterated_name = translit(self.name, 'ru', reversed=True)
            self.slug = slugify(transliterated_name)
        super(ProductCategory, self).save(*args, **kwargs)

    def get_subcategories(self):
        return ProductSubCategory.objects.filter(parent_category=self)

    def __str__(self):
        return self.name


class ProductSubCategory(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    parent_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='subcategory_images/', null=True, blank=True)
    is_index_banner = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'

    def save(self, *args, **kwargs):
        if not self.slug:
            transliterated_name = translit(self.name, 'ru', reversed=True)
            self.slug = slugify(transliterated_name)
        super(ProductSubCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=128)

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=128)
    description = RichTextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1000000)
    quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products_images/', default='site_assets/product_image_plug.jpg', blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, max_length=120)
    updated_at = models.DateTimeField(auto_now=True)
    is_new = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag)
    discount_percentage = models.PositiveIntegerField(default=0)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, editable=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, editable=False)
    article_number = models.CharField(max_length=11, unique=True, editable=False, null=True)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'product_slug': self.slug, 'product_id': self.id})

    def save(self, *args, **kwargs):

        if self.discount_percentage > 0:
            self.discount_price = self.calculate_discounted_price()
        else:
            self.discount_price = None

        if self.discount_price is not None and self.discount_price > 0:
            self.total_price = self.discount_price
        else:
            self.total_price = self.price

        if not self.slug:
            transliterated_name = translit(self.name, 'ru', reversed=True)
            self.slug = slugify(transliterated_name)

        if self.id and not self.article_number:
            category_id = str(self.category.id).zfill(2)
            sub_category_id = str(self.sub_category.id).zfill(2)
            product_id = str(self.id).zfill(5)
            self.article_number = f"{category_id}{sub_category_id}{product_id}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Продукт: {self.name} | Категория: {self.category} | Подкатегория: {self.sub_category}'

    def calculate_discounted_price(self):
        if self.discount_percentage > 0:
            discounted_price = Decimal(self.price) * (1 - Decimal(self.discount_percentage) / 100)
            return discounted_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return None


@receiver(post_save, sender=Product)
def check_image(sender, instance, **kwargs):
    if instance.image and os.path.basename(instance.image.path) != 'product_image_plug.webp':
        img = Image.open(instance.image.path)

        aspect_ratio = img.width / img.height
        size_condition = img.width >= 500 and img.height >= 500

        if aspect_ratio != 1 or not size_condition:
            invalid_images_path = os.path.join('media', 'invalid_images', 'product_invalid_images.txt')
            with open(invalid_images_path, 'a') as file:
                file.write(instance.image.path + '\n')

            instance.image = 'site_assets/product_image_plug.jpg'
            instance.save()


class ProductCharacteristic(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='characteristics')
    name = models.CharField(max_length=120)
    value = models.CharField(max_length=800)

    def __str__(self):
        return f"{self.name}: {self.value}"


class AlterImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='alter_image')
    image = models.ImageField(upload_to='product_alter_images/', blank=True)

    def __str__(self):
        return f'{self.product.name} - {self.image}'


class BasketQuerySet(models.QuerySet):
    def total_sum(self):
        return sum(basket.sum() for basket in self)

    def total_quantity(self):
        return sum(basket.quantity for basket in self)


class Basket(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=0)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    objects = BasketQuerySet.as_manager()

    def __str__(self):
        return f'Корзина для: {self.user.email} | Продукт: {self.product.name}'

    def sum(self):
        return self.product.total_price * self.quantity

    def de_json(self):
        basket_item = {
            'product_name': self.product.name,
            'quantity': self.quantity,
            'price': float(self.product.price),
            'sum': float(self.sum()),
        }
        return basket_item


class ComparisonList(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)

    class Meta:
        verbose_name = 'Список сравнения'
        verbose_name_plural = 'Списки сравнения'

    def __str__(self):
        product_list = ", ".join(str(product) for product in self.products.all())
        return f"ComparisonList (ID: {self.id}, Session ID: {self.session_id}, Products: {product_list})"


class FeaturedProducts(models.Model):
    products = models.ManyToManyField(Product, related_name='featured_products')

    class Meta:
        verbose_name = 'Особый товар'
        verbose_name_plural = 'Особые товары'

    def __str__(self):
        return "Featured Products"


class FeaturedSubcategory(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)
    subcategory = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='special_subcategories/')

    class Meta:
        verbose_name = 'Особая подкатегория'
        verbose_name_plural = 'Особые подкатегории'

    def __str__(self):        return self.subcategory.name

