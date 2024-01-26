from urllib.parse import urlparse

from seo_manager.models import SEOAttributes
from products.models import ProductSubCategory, ProductCategory, Product
from blog.models import Article


def get_seo_attributes(request):
    full_url = request.build_absolute_uri()
    parsed_url = urlparse(full_url)

    domain_name = parsed_url.scheme + '://' + parsed_url.netloc
    path = parsed_url.path
    clear_path = path[4:]
    path_parts = [part for part in clear_path.split('/') if part]

    result = {}
    if path_parts[0] == 'index':
        try:
            seo_attr = SEOAttributes.objects.get(page_url=domain_name+'/')
            result['seo_title'] = seo_attr.title
            result['seo_meta_description'] = seo_attr.meta_description
        except:
            pass
        return result

    if path_parts[0] in ['catalog', 'blog']:
        try:
            seo_attr = SEOAttributes.objects.get(page_url=domain_name+clear_path)
            if seo_attr.title != '' and seo_attr.meta_description != '':
                result['seo_title'] = seo_attr.title
                result['seo_meta_description'] = seo_attr.meta_description
            else:
                if len(path_parts) >= 2 and path_parts[0] == 'catalog':
                    if len(path_parts) == 3 and not path_parts[2].isdigit():
                        sub_category = ProductSubCategory.objects.get(slug=path_parts[2])
                        result['seo_title'] = f'{sub_category.name} - купить c доставкой на дом | IMSOUND.ru'
                        result['seo_meta_description'] = f'На нашем сайте вы можете купить {sub_category.name} c доставкой на дом | IMSOUND.ru'
                    elif len(path_parts) == 2:
                        category = ProductCategory.objects.get(slug=path_parts[1])
                        result['seo_title'] = f'{category.name} - купить c доставкой на дом | IMSOUND.ru'
                        result['seo_meta_description'] = f'На нашем сайте вы можете купить {category.name} c доставкой на дом | IMSOUND.ru'
                    elif len(path_parts) == 3 and path_parts[2].isdigit():
                        product = Product.objects.get(id=path_parts[2])
                        result['seo_title'] = f'{product.name} - купить c доставкой на дом | IMSOUND.ru'
                        result['seo_meta_description'] = f'На нашем сайте вы можете купить {product.name} c доставкой на дом | IMSOUND.ru'
                elif path_parts == ['blog']:
                    result['seo_title'] = f'Блог о световом и музыкальном оборудовани | IMSOUND.ru'
                    result['seo_meta_description'] = f'Тут вы можете найти полезные статьи о профессиональном световом и музыкальном оборудовании | IMSOUND.ru'
                elif len(path_parts) >= 2 and path_parts[:2] == ['blog', 'article']:
                    article = Article.objects.get(slug=path_parts[2])
                    result['seo_title'] = f'{article.title} читать в блоге | IMSOUND.ru'
                    result['seo_meta_description'] = f'Узнайте все об {article.title} в статье нашего блога  | IMSOUND.ru'

        except SEOAttributes.DoesNotExist:
            result = {}
    else:
        result = {}

    return result