import os

from seo_manager.models import SEOAttributes


def get_seo_attributes(set_params):
    url_full = os.getenv('FRONTEND_BASE') + set_params['url'][4:]
    brandname = os.getenv('BRANDNAME')
    page_type = set_params['page_type']
    if page_type == 'catalog':
        return {'title': 'Catalog Default Title', 'meta_description': 'Catalog meta_description Default'}
    elif page_type not in ['info', 'cart', 'checkout', 'profile', 'catalog']:
        try:
            seo_attr_db = SEOAttributes.objects.get(page_url=url_full)
            seo_attr_res = {'title': seo_attr_db.title, 'meta_description': seo_attr_db.meta_description}
        except:
            seo_attr_res = {'title': '', 'meta_description': ''}
    else:
        seo_attr_res = {'title': '', 'meta_description': ''}

    if not seo_attr_res['title']:
        if page_type == 'category':
            seo_attr_res['title'] = f'{set_params["category_name"]} - купить c доставкой на дом | '
        elif page_type == 'subcategory':
            seo_attr_res['title'] = f'{set_params["subcategory_name"]} - купить c доставкой на дом | '
        elif page_type == 'product':
            seo_attr_res['title'] = f'{set_params["product_name"]} - купить {set_params["subcategory_name"]} c доставкой на дом | '
        elif page_type == 'tag':
            seo_attr_res['title'] = f'{set_params["tag_name"]} - купить c доставкой на дом | '
        elif page_type == 'blog':
            seo_attr_res['title'] = f'Блог интернет-магазина | '
        elif page_type == 'article':
            seo_attr_res['title'] = f'{set_params["article_title"]} - смотреть обзоры в блоге | '
        elif page_type == 'info':
            seo_attr_res['title'] = f'Информация об интернет-магазине | '
        elif page_type == 'cart':
            seo_attr_res['title'] = f'Корзина магазина | '
        elif page_type == 'checkout':
            seo_attr_res['title'] = f'Оформление заказа | '
        elif page_type == 'profile':
            seo_attr_res['title'] = f'Личный кабинет | '

    seo_attr_res['title'] += brandname

    if not seo_attr_res['meta_description']:
        if page_type == 'category':
            seo_attr_res['meta_description'] = f'{set_params["category_name"]} meta_description default | '
        elif page_type == 'subcategory':
            seo_attr_res['meta_description'] = f'{set_params["subcategory_name"]} meta_description default | '
        elif page_type == 'product':
            seo_attr_res['meta_description'] = f'{set_params["product_name"]} meta_description default | '
        elif page_type == 'tag':
            seo_attr_res['meta_description'] = f'Tag {set_params["tag_name"]}meta_description default | '
        elif page_type == 'blog':
            seo_attr_res['meta_description'] = f'Блог интернет-магазина meta_description default | '
        elif page_type == 'article':
            seo_attr_res['meta_description'] = f'{set_params["article_title"]} meta_description default'
        elif page_type == 'info':
            seo_attr_res['meta_description'] = f'Информация об интернет-магазине | '
        elif page_type == 'cart':
            seo_attr_res['meta_description'] = f'Корзина магазина | '
        elif page_type == 'checkout':
            seo_attr_res['meta_description'] = f'Оформление заказа | '
        elif page_type == 'profile':
            seo_attr_res['meta_description'] = f'Личный кабинет | '

    seo_attr_res['meta_description'] += brandname

    return seo_attr_res