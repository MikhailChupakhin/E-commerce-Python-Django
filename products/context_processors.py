from products.models import (Basket, Product, ProductCategory,
                             ProductSubCategory)
from seo_manager.models import SEOAttributes


def baskets(request):
    if request.user.is_authenticated:
        baskets = Basket.objects.filter(user=request.user)
        total_sum = None
    else:
        baskets_data = request.session.get('basket', {})
        pseudo_baskets = []
        total_sum = 0

        for product_id, product_data in baskets_data.items():
            product = Product.objects.get(pk=int(product_id))
            pseudo_basket = {
                'product_name': product.name,
                'product_id': int(product_id),
                'quantity': product_data['quantity'],
                'product': product,
                'sum': product.total_price * product_data['quantity'],
            }
            pseudo_baskets.append(pseudo_basket)
            total_sum += pseudo_basket['sum']

        baskets = pseudo_baskets

    return {'baskets': baskets, 'total_sum': total_sum}


def categories_context(request):
    categories = ProductCategory.objects.all()
    return {'categories': categories}


def breadcrumbs(request):
    path_parts = request.path.strip('/').split('/')
    unwanted_parts = ['users', 'profile', 'order', 'orders', 'cart', 'page', 'tag', 'info']
    path_parts = [part for part in path_parts if part not in unwanted_parts]

    breadcrumbs = [('/', 'Главная')]

    url_so_far = ''
    for i in range(len(path_parts)):
        url_part = path_parts[i]
        if url_part == 'products':
            breadcrumbs.append(('/products', 'Каталог'))
            url_so_far = '/products'
        else:
            try:
                category = ProductCategory.objects.get(slug=url_part)
                part_name = category.name
            except ProductCategory.DoesNotExist:
                try:
                    subcategory = ProductSubCategory.objects.get(slug=url_part)
                    part_name = subcategory.name
                except ProductSubCategory.DoesNotExist:
                    part_name = url_part

            url_so_far += f'/{url_part}'
            breadcrumbs.append((url_so_far, part_name))

    if len(breadcrumbs) > 1:
        del breadcrumbs[-1]

    return {
        'breadcrumbs': breadcrumbs,
    }


def seo_attributes(request):
    try:
        full_url = request.build_absolute_uri()
        seo_attr = SEOAttributes.objects.get(page_url=full_url)
        return {'seo_title': seo_attr.title, 'seo_meta_descrition': seo_attr.meta_description}
    except SEOAttributes.DoesNotExist:
        return {'seo_title': None, 'seo_meta_descrition': None}
