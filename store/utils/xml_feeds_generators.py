import os

from django.http import HttpResponse
from django.template import loader
from django.utils import timezone

from products.models import ProductCategory, Product

DOMAIN_NAME = os.getenv('DOMAIN_NAME')


def generate_xml_yandex(request):
    # Получаем текущую дату и время
    current_datetime = timezone.now().strftime('%Y-%m-%dT%H:%M:%S%z')
    # Получаем все категории
    categories = ProductCategory.objects.all()

    # Получаем все товары
    products = Product.objects.all()

    # Загружаем шаблон
    template = loader.get_template('xml_templates/yandex.xml')

    # Заполняем контекст шаблона
    context = {
        'current_datetime': current_datetime,
        'DOMAIN_NAME': DOMAIN_NAME,
        'categories': categories,
        'products': products,
    }

    # Рендерим XML
    xml_content = template.render(context)

    # Возвращаем HTTP-ответ с XML-фидом
    response = HttpResponse(xml_content, content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename="feed_yandex.xml"'
    return response


def generate_xml_google(request):
    pass