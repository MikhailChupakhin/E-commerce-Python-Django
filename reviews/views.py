import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, ListView
from rest_framework import status
from rest_framework.response import Response

from api.serializers.reviews_serializers import BlogCommentSerializer
from blog.models import Article
from products.models import Product
from products.views import BaseView
from reviews.forms import ProductReviewForm
from reviews.models import BlogComment, ProductReview
from users.models import User


class AddProductReviewView(BaseView, CreateView):
    model = ProductReview
    form_class = ProductReviewForm
    template_name = 'reviews/review_form.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['category_slug']
        subcategory_slug = self.kwargs['subcategory_slug']
        product_slug = self.kwargs['product_slug']
        context['product'] = get_object_or_404(
            Product,
            category__slug=category_slug,
            sub_category__slug=subcategory_slug,
            slug=product_slug
        )
        return context

    def form_valid(self, form):
        category_slug = self.kwargs['category_slug']
        subcategory_slug = self.kwargs['subcategory_slug']
        product_slug = self.kwargs['product_slug']
        product = get_object_or_404(
            Product,
            category__slug=category_slug,
            sub_category__slug=subcategory_slug,
            slug=product_slug
        )
        review = form.save(commit=False)
        review.product = product
        if self.request.user.is_authenticated:
            review.user = self.request.user
        else:
            review.user = None
        review.rating = int(form.cleaned_data['rating'])
        review.pros = form.cleaned_data['pros']
        review.cons = form.cleaned_data['cons']
        review.text_comment = form.cleaned_data['text_comment']
        review.save()

        return redirect(reverse('products:product_detail', args=[category_slug, subcategory_slug, product_slug]))

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class CreateBlogCommentView(View):
    def post(self, request):
        post_data = json.loads(request.body.decode("utf-8"))
        user_id = post_data.get("user_id")
        text = post_data.get("text")
        article_id = post_data.get("article_id")

        try:
            user = User.objects.get(id=user_id)
            article = Article.objects.get(id=article_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "Пользователь или статья не найдены."}, status=404)

        comment = BlogComment(user=user, article=article, text=text, moderated=False)
        comment.save()

        return JsonResponse({"message": "Комментарий успешно отправлен на модерацию."})

    def get(self, request):
        return JsonResponse({"error": "Метод запроса не поддерживается."}, status=400)


