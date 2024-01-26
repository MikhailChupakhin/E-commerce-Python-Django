from django.shortcuts import get_object_or_404

from products.models import (Product, ProductCategory,
                             ProductSubCategory)


def get_breadcrumbs(request):
    path_parts = request.path.strip('/').split('/')
    unwanted_parts = ['api', 'users', 'profile', 'order', 'orders', 'cart', 'page', 'tag', 'info']
    path_parts = [part for part in path_parts if part not in unwanted_parts]

    breadcrumbs = [('/', 'Главная')]

    if 'catalog' in path_parts:
        breadcrumbs.append(('/catalog', 'Каталог'))
        url_so_far = '/catalog'

        try:
            product_id = int(path_parts[2])
            product = get_object_or_404(Product, id=product_id)
            category_name = product.category.name
            url_so_far += f'/{product.category.slug}'
            breadcrumbs.append((url_so_far, category_name))
            subcategory_name = product.sub_category.name
            url_so_far += f'/{product.sub_category.slug}'
            breadcrumbs.append((url_so_far, subcategory_name))
            breadcrumbs.append((f'/catalog/{product.slug}/{product.id}', product.name))
        except:
            if len(path_parts) == 2:
                category = ProductCategory.objects.get(slug=path_parts[1])
                category_name = category.name
                breadcrumbs.append((f'/catalog/{category_name}/', category_name))
            elif len(path_parts) == 3:
                category = ProductCategory.objects.get(slug=path_parts[1])
                category_name = category.name
                breadcrumbs.append((f'/catalog/{category.slug}/', category_name))
                sub_category = ProductSubCategory.objects.get(slug=path_parts[2])
                subcategory_name = sub_category.name
                breadcrumbs.append((f'/catalog/{category.slug}/{sub_category.slug}/', subcategory_name))

    # Доделать блок для блога

    if request.path == '/api/orders/checkout/':
        if request.user.is_authenticated:
            breadcrumbs.append(('/users/cart/', 'Корзина'))
        else:
            breadcrumbs.append(('/users/cart_guest/', 'Корзина'))

    return breadcrumbs

