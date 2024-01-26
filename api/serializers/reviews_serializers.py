from rest_framework import serializers
from reviews.models import ProductReview, BlogComment


class ProductReviewSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = ProductReview
        fields = ['product_id', 'rating', 'pros', 'cons', 'text_comment']


class BlogCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogComment
        fields = ['article', 'text']
