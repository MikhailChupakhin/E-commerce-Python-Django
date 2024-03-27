from rest_framework import serializers
from seo_manager.models import InfoPage, SEOAttributes, SliderImage, Tag, Redirect


class InfoPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoPage
        fields = '__all__'


class SEOAttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEOAttributes
        fields = '__all__'


class SliderImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SliderImage
        fields = ['id', 'image', 'subtitle', 'subtitle', 'alt_text']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RedirectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redirect
        fields = '__all__'
