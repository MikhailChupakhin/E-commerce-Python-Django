from django.contrib.auth.views import LogoutView
from django.urls import path

from .views.blog_views import BlogIndexAPIView, ArticleDetailAPIView, TagArticlesListAPIView, \
    CategoryArticlesListAPIView
from .views.orders_views import CheckoutAUTHAPIView, OrderDetailAPIView, OrderListAPIView, CheckoutGuestAPIView
from .views.products_views import (BaseAPIView, IndexAPIView, ProductsListAPIView, CategoryProductsListAPIView,
                                   SubcategoryProductsListAPIView, TagProductsAPIView,
                                   ProductSearchAPIView, DiscountedProductsAPIView, ProductDetailAPIView,
                                   BuyInOneClickAPIView, BasketAddAPIView, BasketAddGuestAPIView,
                                   ChangeComparisonAPIView, ComparisonAPIView, ProductQuickviewAPIView)
from .views.reviews_views import AddProductReviewAPIView, CreateBlogCommentAPIView
from .views.token_views import CustomTokenObtainPairView
from .views.users_views import UserLoginAPIView, UserRegistrationAPIView, UserProfileAPIView, UserCartAPIView, \
    UserCartRemoveAPIView, UserCartUpdateAPIView, GuestCartAPIView, GuestCartRemoveAPIView, GuestCartUpdateAPIView, \
    SaveDeliveryAUTHUserAPIView, SaveDeliveryNOAUTHUserAPIView, EmailVerificationAPIView, CreateCallbackQueryAPIView, SubscribeNewsAPIView, \
    ApplyPromoCodeAPIView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'api'


urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('base/', BaseAPIView.as_view(), name='base-api'),
    path('index/', IndexAPIView.as_view(), name='index-api'),
    path('comparison/', ComparisonAPIView.as_view(), name='comparison'),
    path('change_comparison/', ChangeComparisonAPIView.as_view(), name='change_comparison'),
    path('catalog/', ProductsListAPIView.as_view(), name='index'),
    path('baskets/add/', BasketAddAPIView.as_view(), name='basket_add'),
    path('baskets/add-guest/', BasketAddGuestAPIView.as_view(), name='basket_add_guest'),
    path('buy_in_one_click/', BuyInOneClickAPIView.as_view(), name='buy_in_one_click'),
    path('search/', ProductSearchAPIView.as_view(), name='product_search'),
    path('discount/', DiscountedProductsAPIView.as_view(), name='discount'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('catalog/<slug:product_slug>/<int:product_id>/', ProductDetailAPIView.as_view(), name='product_detail'),
    path('catalog/<slug:category_slug>/', CategoryProductsListAPIView.as_view(), name='category'),
    path('catalog/tags/<slug:tag_slug>/', TagProductsAPIView.as_view(), name='tag_products'),
    path('catalog/<slug:category_slug>/<slug:subcategory_slug>/', SubcategoryProductsListAPIView.as_view(), name='subcategory'),
    path('users/login/', UserLoginAPIView.as_view(), name='user-login-api'),
    path('users/register/', UserRegistrationAPIView.as_view(), name='user-registration-api'),
    path('users/verify/<str:email>/<uuid:code>/', EmailVerificationAPIView.as_view(), name='email_verification'),
    path('users/profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('users/cart/', UserCartAPIView.as_view(), name='cart'),
    path('users/cart/remove/', UserCartRemoveAPIView.as_view(), name='cart_remove'),
    path('users/cart/update/', UserCartUpdateAPIView.as_view(), name='cart_update'),
    path('users/cart-guest/', GuestCartAPIView.as_view(), name='cart_guest'),
    path('users/cart-guest/remove/', GuestCartRemoveAPIView.as_view(), name='cart_guest_remove'),
    path('users/cart-guest/update/', GuestCartUpdateAPIView.as_view(), name='cart_guest_update'),
    path('users/save_delivery_auth/', SaveDeliveryAUTHUserAPIView.as_view(), name='save_delivery'),
    path('users/save_delivery_noauth/', SaveDeliveryNOAUTHUserAPIView.as_view(), name='save_delivery_noauth'),
    path('users/callback/', CreateCallbackQueryAPIView.as_view(), name='create-callback-query'),
    path('users/subscribe_news/', SubscribeNewsAPIView.as_view(), name='subscribe_news'),
    path('users/apply_promo_code/', ApplyPromoCodeAPIView.as_view(), name='apply_promo_code'),
    path('blog/', BlogIndexAPIView.as_view(), name='blog_index'),
    path('blog/article/<slug:slug>/', ArticleDetailAPIView.as_view(), name='article_detail'),
    path('blog/<slug:tag_slug>/', TagArticlesListAPIView.as_view(), name='tag_articles'),
    path('blog/category/<slug:category_slug>/', CategoryArticlesListAPIView.as_view(), name='category_articles'),
    path('reviews/add_review/', AddProductReviewAPIView.as_view(), name='add_review'),
    path('reviews/create_comment/', CreateBlogCommentAPIView.as_view(), name='create_comment'),
    path('orders/checkout/auth/', CheckoutAUTHAPIView.as_view(), name='checkout'),
    path('orders/checkout/guest/', CheckoutGuestAPIView.as_view(), name='checkout_guest'),
    path('orders/<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path('orders/my-list/', OrderListAPIView.as_view(), name='orders_list'),
    path('product/quick-view/<int:product_id>/', ProductQuickviewAPIView.as_view(), name='quick-view'),
]