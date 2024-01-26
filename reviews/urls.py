from django.urls import path

from reviews.views import AddProductReviewView, CreateBlogCommentView

app_name = 'reviews'


urlpatterns = [
    path('<slug:category_slug>/<slug:subcategory_slug>/<slug:product_slug>/add_review/', AddProductReviewView.as_view(), name='add_review'),
    path('create_comment/', CreateBlogCommentView.as_view(), name='create_comment'),
]
