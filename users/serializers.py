from rest_framework import serializers

from .models import CallbackQuery


class CallbackQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = CallbackQuery
        fields = ('name', 'phone')