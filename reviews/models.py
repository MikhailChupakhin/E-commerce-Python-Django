import hashlib

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from blog.models import Article
from products.models import Product
from users.models import User


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveIntegerField(default=5)
    pros = models.TextField(max_length=120, blank=True)
    cons = models.TextField(max_length=120, blank=True)
    text_comment = models.TextField(max_length=1000, blank=True)
    moderated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отзыв о товаре'
        verbose_name_plural = 'Отзывы о товарах'


class BlogComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    text = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    moderated = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Комментарий к статье'
        verbose_name_plural = 'Комментарии к статьям'

    def __str__(self):
        return f'Комментарий от {self.user} к статье "{self.article}"'

