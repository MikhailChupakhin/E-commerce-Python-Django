from django.contrib import admin

from .models import BlogComment, ProductReview


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'moderated', 'rating', 'product', 'user')
    list_filter = ('product', 'moderated')
    search_fields = ('user__username', 'user_name', 'product__name')

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'article', 'created_at', 'moderated', 'user')
    list_filter = ('moderated',)
