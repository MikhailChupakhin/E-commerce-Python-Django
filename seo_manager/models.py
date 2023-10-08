from django.utils.text import slugify
from transliterate import translit
from django.db import models
from ckeditor.fields import RichTextField


class InfoPage(models.Model):
    SECTION_CHOICES = (
        (1, 'Компания'),
        (2, 'Клиентам'),
    )

    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    content = RichTextField()
    section = models.IntegerField(choices=SECTION_CHOICES)

    class Meta:
        verbose_name = 'Инфо-страница'
        verbose_name_plural = 'Инфо-страницы'

    def __str__(self):
        return self.title


class SEOAttributes(models.Model):
    page_url = models.TextField(unique=True)
    title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    alt_image = models.CharField(max_length=200, default='', blank=True)

    class Meta:
        verbose_name = 'SEO-атрибут'
        verbose_name_plural = 'SEO-атрибуты'

    def __str__(self):
        return self.page_url


class SliderImage(models.Model):
    image = models.ImageField(upload_to='slider_images/')
    title = models.CharField(max_length=120, blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Слайд'
        verbose_name_plural = 'Слайды'

    def __str__(self):
        return self.alt_text


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        if not self.slug:
            transliterated_name = translit(self.name, 'ru', reversed=True)
            self.slug = slugify(transliterated_name)

        super().save(*args, **kwargs)


class Redirect(models.Model):
    old_path = models.CharField(max_length=200, unique=True)
    new_path = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now=True)

