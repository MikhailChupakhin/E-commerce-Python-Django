from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product, ProductCategory, ProductSubCategory


class IndexSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return ['index']

    def location(self, item):
        return reverse(item)


class ProductsPageSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return ['products:index']

    def location(self, item):
        return reverse(item)


class ProductsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Product.objects.order_by('updated_at')

    def get_paginated_response(self, *args, **kwargs):
        return self.items()

    def location(self, obj):
        return reverse('products:product_detail', kwargs={
            'product_slug': obj.slug,
            'product_id': obj.id,
        })

    def lastmod(self, obj):
        return obj.updated_at


class ProductCategorySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return ProductCategory.objects.order_by('id')

    def location(self, item):
        return reverse('products:category', kwargs={'category_slug': item.slug})


class ProductSubCategorySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return ProductSubCategory.objects.order_by('id')

    def location(self, item):
        return reverse('products:subcategory', kwargs={
            'category_slug': item.parent_category.slug,
            'subcategory_slug': item.slug,
        })