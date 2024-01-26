from ckeditor.fields import RichTextField
from django.db import models
from django.utils.text import slugify
from transliterate import translit


class BlogCategory(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = 'Категория блога'
        verbose_name_plural = 'Категории блога'

    def save(self, *args, **kwargs):
        if not self.slug:
            transliterated_title = translit(self.title, 'ru', reversed=True)
            self.slug = slugify(transliterated_title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class BlogTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    class Meta:
        verbose_name = 'Тэг блога'
        verbose_name_plural = 'Тэги блога'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            transliterated_name = translit(self.name, 'ru', reversed=True)
            self.slug = slugify(transliterated_name)

        super().save(*args, **kwargs)


class Article(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=30)
    image = models.ImageField(upload_to='blog/images/', blank=True)
    content = RichTextField()
    created_timestamp = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    main_tag = models.ForeignKey(BlogTag, on_delete=models.SET_NULL, null=True, blank=True, related_name='main_tag')
    tags = models.ManyToManyField(BlogTag)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='articles')
    views_counter = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return f'Статья: "{self.title}"'

    def save(self, *args, **kwargs):
        if not self.slug:
            transliterated_title = translit(self.title, 'ru', reversed=True)
            self.slug = slugify(transliterated_title)

        super().save(*args, **kwargs)

    def increment_views(self, request):
        viewed_articles = request.session.get('viewed_articles', [])

        if self.pk not in viewed_articles:
            self.views_counter += 1
            self.save()

            viewed_articles.append(self.pk)
            request.session['viewed_articles'] = viewed_articles
