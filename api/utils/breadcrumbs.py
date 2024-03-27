def get_breadcrumbs(set_params):
    page_type = set_params['page_type']
    path_parts = set_params['url'].strip('/').split('/')
    breadcrumbs = [('/', 'Главная')]
    catalog_crumb = ('catalog', 'Каталог')

    if page_type == 'catalog':
        return [('/', 'Главная'), catalog_crumb]
    elif page_type == 'category':
        breadcrumbs.append(catalog_crumb)
        breadcrumbs.append((f'{set_params["url"]}', f'{set_params["category_name"]}'))
    elif page_type == 'subcategory':
        breadcrumbs.append(catalog_crumb)
        breadcrumbs.append((f'/{path_parts[1]}/{path_parts[2]}/', f'{set_params["category_name"]}'))
        breadcrumbs.append((f'/{path_parts[1]}/{path_parts[2]}/{path_parts[3]}/', f'{set_params["subcategory_name"]}'))
    elif page_type == 'product':
        breadcrumbs.append(catalog_crumb)
        breadcrumbs.append((f'/catalog/{set_params["category_slug"]}/', f'{set_params["category_name"]}'))
        breadcrumbs.append((f'/catalog/{set_params["category_slug"]}/{set_params["subcategory_slug"]}/', f'{set_params["subcategory_name"]}'))
        breadcrumbs.append((f'/catalog/{set_params["product_slug"]}/{set_params["product_id"]}/', f'{set_params["product_name"]}'))
    elif page_type == 'tag':
        breadcrumbs.append(catalog_crumb)
        breadcrumbs.append((f'/catalog/tags/{path_parts[2]}', f'{set_params["tag_name"]}'))
    elif page_type == 'blog':
        pass
    elif page_type == 'article':
        pass
    elif page_type == 'info':
        pass
    elif page_type == 'cart':
        breadcrumbs.append(catalog_crumb)
        breadcrumbs.append((f'/users/cart', f'Корзина'))
    elif page_type == 'checkout':
        pass
    elif page_type == 'profile':
        pass

    return breadcrumbs

