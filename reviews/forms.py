from django import forms

from reviews.models import ProductReview


class ProductReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        label="Рейтинг",
        min_value=1,
        max_value=5,
    )
    pros = forms.CharField(
        label="Достоинства",
        max_length=120,
        widget=forms.Textarea(attrs={'placeholder': 'Достоинства товара'}),
        required=False,
    )
    cons = forms.CharField(
        label="Недостатки",
        max_length=120,
        widget=forms.Textarea(attrs={'placeholder': 'Недостатки товара'}),
        required=False,
    )
    text_comment = forms.CharField(
        label="Комментарий",
        max_length=1000,
        widget=forms.Textarea(attrs={'placeholder': 'Ваш комментарий'}),
        required=False,
    )

    class Meta:
        model = ProductReview
        fields = []
