from django import forms


class ProductFilterForm(forms.Form):
    min_price = forms.DecimalField(label='Минимальная цена', required=False)
    max_price = forms.DecimalField(label='Максимальная цена', required=False)

