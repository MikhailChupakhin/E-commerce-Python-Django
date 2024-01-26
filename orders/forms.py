import json

from django import forms

from .models import PROVINCE_CHOICES, DeliveryMethod, Order, PaymentMethod


class OrderForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иван'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'example@example.ru'
    }))
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Город'}))
    province = forms.ChoiceField(
        choices=PROVINCE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Россия, г.Москва, ул.Пушкина, дом Колотушкина, кв.110'
    }))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Формат: 81234567890 или +71234567890'}))
    aux_phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Дополнительный номер телефона'}), required=False)
    company = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Компания'}), required=False)
    zipcode = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Индекс'}), required=False)
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.filter(is_active=True),
        widget=forms.RadioSelect(attrs={'class': 'form-select'}),
    )
    delivery_method = forms.ModelChoiceField(
        queryset=DeliveryMethod.objects.filter(is_active=True),
        widget=forms.HiddenInput  # Скрываем поле
    )

    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'email', 'address', 'phone', 'payment_method', 'delivery_method')

