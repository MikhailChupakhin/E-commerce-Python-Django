from django.shortcuts import render
from django.views.generic.base import TemplateView
from .models import InfoPage
from products.views import BaseView


class InfoPageView(TemplateView):
    template_name = "seo_manager/info_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs['slug']
        info_page = InfoPage.objects.get(slug=slug)
        context['info_page'] = info_page
        context['company_info'] = InfoPage.objects.filter(section=1).values('title', 'slug')
        context['clients_info'] = InfoPage.objects.filter(section=2).values('title', 'slug')

        return context