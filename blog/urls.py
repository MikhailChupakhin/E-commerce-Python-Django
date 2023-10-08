from django.urls import path

from .views import (ArticleDetailView, BlogIndexView, CategoryArticlesListView,
                    TagArticlesListView)

app_name = 'blog'


urlpatterns = [
    path('', BlogIndexView.as_view(), name='blog_index'),
    path('article/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    path('<slug:tag_slug>/', TagArticlesListView.as_view(), name='tag_articles'),
    path('category/<slug:category_slug>/', CategoryArticlesListView.as_view(), name='category_articles'),
]
