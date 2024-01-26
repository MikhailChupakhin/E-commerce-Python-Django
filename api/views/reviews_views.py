from django.urls import reverse
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from api.serializers.reviews_serializers import ProductReviewSerializer, BlogCommentSerializer
from blog.models import Article
from products.models import Product
from reviews.models import BlogComment
from users.models import User


@permission_classes([permissions.IsAuthenticated])
class AddProductReviewAPIView(generics.CreateAPIView):
    serializer_class = ProductReviewSerializer

    def perform_create(self, serializer):
        product_id = serializer.validated_data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        serializer.save(
            product=product,
            user=self.request.user if self.request.user.is_authenticated else None,
            rating=int(serializer.validated_data['rating']),
        )

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response({'message': 'Отзыв был успешно добавлен и ожидает модерации.'})
        except Exception as e:
            return Response({'message': 'При добавлении отзыва произошла ошибка'})



@permission_classes([permissions.IsAuthenticated])
class CreateBlogCommentAPIView(APIView):
    def post(self, request):
        serializer = BlogCommentSerializer(data=request.data)

        if serializer.is_valid():
            article = serializer.validated_data.get("article")
            text = serializer.validated_data.get("text")


            article = get_object_or_404(Article, id=article.id)

            comment = BlogComment(user=request.user, article=article, text=text, moderated=False)
            comment.save()

            return Response({"message": "Комментарий успешно отправлен на модерацию."}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response({"error": "Некорректные данные для комментария."}, status=status.HTTP_400_BAD_REQUEST)
