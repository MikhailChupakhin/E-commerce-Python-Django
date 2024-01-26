from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
from django.db import models

from products.models import (AlterImage, Basket, ComparisonList,
                             FeaturedProducts, FeaturedSubcategory,
                             Manufacturer, Product, ProductCategory,
                             ProductCharacteristic, ProductSubCategory)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    fields = ('name', 'slug', 'description')


@admin.register(ProductSubCategory)
class ProductSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent_category', 'image', 'is_index_banner')
    list_filter = ('parent_category',)
    search_fields = ('name',)


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [ProductInline]


class ProductCharacteristicInline(admin.TabularInline):
    model = ProductCharacteristic


class TagInline(admin.TabularInline):
    model = Product.tags.through


class AlterImageInline(admin.TabularInline):
    model = AlterImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'manufacturer', 'article_number', 'slug', 'price', 'discount_percentage', 'total_price', 'quantity',
                    'image', 'category', 'sub_category', 'updated_at')
    readonly_fields = ('discount_price', 'article_number')
    fields = ('image', ('name', 'article_number'), 'manufacturer', 'slug', 'description', ('price', 'quantity',
              'discount_percentage', 'discount_price'), 'category', 'sub_category')
    search_fields = ('name',)
    ordering = ('name', 'manufacturer',)
    inlines = [AlterImageInline, TagInline, ProductCharacteristicInline]

    # Подключение CKEditorWidget к полю description
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},
    }


class BasketAdmin(admin.TabularInline):
    model = Basket
    fields = ('product', 'quantity', 'created_timestamp')
    readonly_fields = ('created_timestamp',)
    extra = 0


class ComparisonListAdmin(admin.ModelAdmin):

    list_display = ['id', 'session', 'get_products_count']

    def get_products_count(self, obj):
        return obj.products.count()
    get_products_count.short_description = 'Количество продуктов'


admin.site.register(ComparisonList, ComparisonListAdmin)


class FeaturedProductsForm(forms.ModelForm):
    class Meta:
        model = FeaturedProducts
        fields = '__all__'


@admin.register(FeaturedProducts)
class FeaturedProductsAdmin(admin.ModelAdmin):
    form = FeaturedProductsForm


@admin.register(FeaturedSubcategory)
class FeaturedSubcategoryAdmin(admin.ModelAdmin):
    list_display = ('subcategory', 'name', 'image')
    raw_id_fields = ('subcategory',)
    fields = ('subcategory', 'name', 'image',)
