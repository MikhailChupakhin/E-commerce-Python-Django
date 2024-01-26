from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from api.serializers.blog_serializers import ArticleSerializer, BlogTagSerializer, BlogCategorySerializer
from api.serializers.reviews_serializers import BlogCommentSerializer
from api.views.products_views import BaseAPIView
from blog.models import Article, BlogCategory, BlogTag
from reviews.models import BlogComment


class BlogIndexAPIView(BaseAPIView):
    articles_per_page = 9

    def get(self, request):
        base_data = self.get_context()

        articles = Article.objects.all().order_by('-created_timestamp')

        paginator = PageNumberPagination()
        paginator.page_size = self.articles_per_page
        result_page = paginator.paginate_queryset(articles, request)

        serializer = ArticleSerializer(result_page, many=True)

        response_data = {
            'base_data': base_data,
            'pagination': {
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'results': serializer.data,
            }
        }

        return Response(response_data)


class ArticleDetailAPIView(BaseAPIView):
    def get(self, request, slug):
        base_data = self.get_context()
        article = get_object_or_404(Article, slug=slug)
        article.increment_views(request)
        all_tags = BlogTag.objects.all()
        blog_categories = BlogCategory.objects.annotate(num_articles=Count('articles'))

        total_article_count = 0
        for category in blog_categories:
            total_article_count += category.num_articles

        top_articles = Article.objects.order_by('-views_counter')[:5]
        related_articles = Article.objects.filter(category=article.category).exclude(slug=slug).order_by(
            '-created_timestamp')
        comments = BlogComment.objects.filter(article=article, moderated=True).order_by('-created_at')

        # Сериализация данных
        article_serializer = ArticleSerializer(article)
        tag_serializer = BlogTagSerializer(all_tags, many=True)
        category_serializer = BlogCategorySerializer(blog_categories, many=True)
        comment_serializer = BlogCommentSerializer(comments, many=True)

        context = {
            'base_data': base_data,
            'article': article_serializer.data,
            'all_tags': tag_serializer.data,
            'blog_categories': category_serializer.data,
            'total_article_count': total_article_count,
            'top_articles': ArticleSerializer(top_articles, many=True).data,
            'comments': comment_serializer.data,
            'related_articles': ArticleSerializer(related_articles, many=True).data,
        }

        return Response(context)


class TagArticlesListAPIView(BaseAPIView):
    articles_per_page = 9

    def get_queryset(self, tag_slug):
        tag = get_object_or_404(BlogTag, slug=tag_slug)
        return Article.objects.filter(tags__in=[tag]).order_by('-created_timestamp')

    def get(self, request, tag_slug, format=None):
        base_data = self.get_context()
        articles = self.get_queryset(tag_slug)
        paginator = PageNumberPagination()
        paginator.page_size = self.articles_per_page
        result_page = paginator.paginate_queryset(articles, request)

        serializer = ArticleSerializer(result_page, many=True)

        response_data = {
            'base_data': base_data,
            'pagination': {
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'results': serializer.data,
            }
        }

        return Response(response_data)


class CategoryArticlesListAPIView(BaseAPIView):
    articles_per_page = 9

    def get_queryset(self, category_slug):
        return Article.objects.filter(category__slug=category_slug).order_by('-created_timestamp')

    def get(self, request, category_slug, format=None):
        base_data = self.get_context()
        articles = self.get_queryset(category_slug)
        paginator = PageNumberPagination()
        paginator.page_size = self.articles_per_page
        result_page = paginator.paginate_queryset(articles, request)

        serializer = ArticleSerializer(result_page, many=True)

        response_data = {
            'base_data': base_data,
            'pagination': {
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'results': serializer.data,
            }
        }

        return Response(response_data)