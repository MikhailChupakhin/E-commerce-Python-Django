from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import ListView

from reviews.models import BlogComment

from .models import Article, BlogCategory, BlogTag


class BlogIndexView(View):
    template_name = 'blog/blog_index.html'
    articles_per_page = 9

    def get(self, request):
        articles = Article.objects.all().order_by('-created_timestamp')
        paginator = Paginator(articles, self.articles_per_page)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)

        context = {
            'page': page,
        }
        return render(request, self.template_name, context)


class ArticleDetailView(View):
    template_name = 'blog/article_detail.html'

    def get(self, request, slug):
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

        context = {
            'article': article,
            'all_tags': all_tags,
            'blog_categories': blog_categories,
            'total_article_count': total_article_count,
            'top_articles': top_articles,
            'comments': comments,
            'related_articles': related_articles,
        }

        return render(request, self.template_name, context)


class TagArticlesListView(ListView):
    model = Article
    template_name = 'blog/blog_index.html'
    context_object_name = 'articles'
    articles_per_page = 9

    def get_queryset(self):
        tag_slug = self.kwargs['tag_slug']
        tag = get_object_or_404(BlogTag, slug=tag_slug)
        return Article.objects.filter(tags__in=[tag]).order_by('-created_timestamp')

    def get(self, request, *args, **kwargs):
        articles = self.get_queryset()
        paginator = Paginator(articles, self.articles_per_page)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)

        context = {
            'page': page,
        }
        return render(request, self.template_name, context)


class CategoryArticlesListView(ListView):
    model = Article
    template_name = 'blog/blog_index.html'
    context_object_name = 'articles'
    articles_per_page = 9

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        return Article.objects.filter(category__slug=category_slug).order_by('-created_timestamp')

    def get(self, request, *args, **kwargs):
        articles = self.get_queryset()
        paginator = Paginator(articles, self.articles_per_page)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)

        context = {
            'page': page,
        }
        return render(request, self.template_name, context)


