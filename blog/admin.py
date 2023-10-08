from ckeditor.widgets import CKEditorWidget
from django.contrib import admin
from django.db import models

from .models import Article, BlogCategory, BlogTag


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'slug')


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'slug', 'main_tag', 'author', 'created_timestamp')
    list_filter = ('created_timestamp',)
    search_fields = ('title', 'author')
    ordering = ('-created_timestamp',)

    # Подключение CKEditorWidget к полю content
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},
    }
