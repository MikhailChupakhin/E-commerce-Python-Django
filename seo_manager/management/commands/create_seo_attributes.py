import xml.etree.ElementTree as ET

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from seo_manager.models import SEOAttributes


class Command(BaseCommand):
    help = 'Create SEOAttributes for all URLs in sitemap'

    def handle(self, *args, **options):
        sitemap_url = settings.SITEMAP_URL
        try:
            response = requests.get(sitemap_url)
            if response.status_code == 200:
                sitemap_content = response.text
                urls = self.extract_urls_from_sitemap(sitemap_content)
                self.create_seo_attributes(urls)
                self.stdout.write(self.style.SUCCESS('SEOAttributes created successfully.'))
            else:
                self.stdout.write(self.style.WARNING(f'Failed to fetch sitemap. Status code: {response.status_code}'))
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Error fetching sitemap: {e}'))

    def extract_urls_from_sitemap(self, sitemap_content):
        urls = []
        try:
            # Разбираем XML-документ
            root = ET.fromstring(sitemap_content)

            # Извлекаем URL-адреса из тегов <url> в sitemap
            for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None and loc_elem.text:
                    urls.append(loc_elem.text)
        except ET.ParseError:
            print("Ошибка разбора XML-документа sitemap")

        return urls

    def create_seo_attributes(self, urls):
        domain = 'http://188.68.221.207'
        for url in urls:
            # Заменим доменное имя на пустую строку
            url_without_domain = url.replace(domain, '', 1)

            try:
                # Получаем SEOAttributes для URL, если объект уже существует, пропускаем, чтобы не дублировать
                seo_attributes = SEOAttributes.objects.get(page_url=url_without_domain)
            except SEOAttributes.DoesNotExist:
                # Если объект не существует, создаем новый экземпляр SEOAttributes с пустыми параметрами.
                seo_attributes = SEOAttributes(page_url=url_without_domain)
                seo_attributes.save()