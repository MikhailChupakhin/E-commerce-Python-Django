from django.db.models import Count

from .models import SEOAttributes, Tag


def seo_attributes(request):
    current_url = request.get_full_path()
    try:
        url = SEOAttributes.objects.get(page_url=current_url)
        context = {
            'seo_attributes': url,
            'title': url.title,
            'meta_description': url.meta_description,
            'alt_image': url.alt_image,
        }
    except SEOAttributes.DoesNotExist:
        context = {'seo_attributes': None}

    return context

def tag_cloud(request):
    popular_tags = Tag.objects.annotate(num_products=Count('product')).order_by('-num_products')[:10]
    return {'popular_tags': popular_tags}

def all_seo_attributes(request):
    all_seo_attributes = SEOAttributes.objects.all()
    return {'all_seo_attributes': all_seo_attributes}