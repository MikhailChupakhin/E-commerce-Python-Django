from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Article, BlogCategory, BlogTag


class BlogIndexSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return ['blog:blog_index']

    def location(self, item):
        return reverse(item)


class BlogCategorySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return BlogCategory.objects.order_by('id')

    def location(self, item):
        return reverse('blog:category_articles', kwargs={'category_slug': item.slug})


class BlogTagSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return BlogTag.objects.order_by('id')

    def location(self, item):
        return reverse('blog:tag_articles', kwargs={'tag_slug': item.slug})


class ArticleSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Article.objects.order_by('created_timestamp')

    def location(self, item):
        return reverse('blog:article_detail', kwargs={'slug': item.slug})
