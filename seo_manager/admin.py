from django.contrib import admin

from .models import Redirect, SEOAttributes, SliderImage, Tag

from .models import InfoPage

@admin.register(InfoPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')


class SEOAttributesAdmin(admin.ModelAdmin):
    list_display = ('page_url', 'title', 'meta_description', 'alt_image')
    list_display_links = ('page_url',)

admin.site.register(SEOAttributes, SEOAttributesAdmin)


class SliderImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'image', 'alt_text', 'is_active',)
    list_display_links = ('title',)

admin.site.register(SliderImage, SliderImageAdmin)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')

admin.site.register(Tag, TagAdmin)


class RedirectAdmin(admin.ModelAdmin):
    list_display = ('old_path', 'new_path', 'created_at')

admin.site.register(Redirect, RedirectAdmin)
