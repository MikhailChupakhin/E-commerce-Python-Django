from django.urls import path

from .views import InfoPageView

app_name = 'seo-manager'


urlpatterns = [
    path('<slug:slug>/', InfoPageView.as_view(), name='info_page'),
]