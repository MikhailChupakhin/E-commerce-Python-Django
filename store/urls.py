from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.static import serve

from blog.sitemaps import (ArticleSitemap, BlogCategorySitemap,
                           BlogIndexSitemap, BlogTagSitemap)
from products.sitemaps import (IndexSitemap, ProductCategorySitemap,
                               ProductsPageSitemap, ProductsSitemap,
                               ProductSubCategorySitemap)
from products.views import IndexView

from .utils.product_management_utils import (export_product_to_xlsx, import_products_from_xlsx,
                                             transfer_products_between_manufacturers)


from .utils.xml_feeds_generators import (generate_xml_yandex, generate_xml_google)
from .utils.seo_management_utils import (CreateSEOAttributesFromSitemapView,
                                         export_seo_to_xlsx,
                                         import_seo_from_xlsx)

from .yasg import urlpatterns as doc_urls

sitemaps = {
    'index': IndexSitemap(),
    'products_page': ProductsPageSitemap,
    'products': ProductsSitemap(),
    'category': ProductCategorySitemap(),
    'sub_category': ProductSubCategorySitemap(),
    'blog_index': BlogIndexSitemap(),
    'blog_category': BlogCategorySitemap(),
    'blog_tag': BlogTagSitemap(),
    'blog_article': ArticleSitemap(),
}


static_urlpatterns = [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('service/products_import/', import_products_from_xlsx, name='products_import_action'),
    path('service/products_export/', export_product_to_xlsx, name='products_export_action'),
    path('service/transfer_products/', transfer_products_between_manufacturers, name='transfer_products'),
    path('service/generate_xml_yandex/', generate_xml_yandex, name='generate_xml_feed_yandex'),
    path('service/generate_xml_google/', generate_xml_google, name='generate_xml_feed_google'),
    path('service/seo_import/', import_seo_from_xlsx, name='seo_import_action'),
    path('service/seo_export/', export_seo_to_xlsx, name='seo_export_action'),
    path('service/generate_urls/', CreateSEOAttributesFromSitemapView.as_view(), name='generate_urls'),
    path('', IndexView.as_view(), name='index'),
    path('info/', include('seo_manager.urls', namespace='seo_manager')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('catalog/', include('products.urls', namespace='products')),
    path('users/', include('users.urls', namespace='users')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('accounts/', include('allauth.urls')),
    path('api/', include('api.urls', namespace='api')),
    path('sitemap.xml', sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path('robots.txt', TemplateView.as_view(template_name="store/robots.txt", content_type="text/plain")),
]

urlpatterns += doc_urls

if settings.DEBUG:
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

