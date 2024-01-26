from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path

from .views.blog_views import BlogIndexAPIView, ArticleDetailAPIView, TagArticlesListAPIView, \
    CategoryArticlesListAPIView
from .views.orders_views import CheckoutAPIView, OrderDetailAPIView, OrderListAPIView
from .views.products_views import (BaseAPIView, IndexAPIView, ProductsListAPIView, CategoryProductsListAPIView,
                                   SubcategoryProductsListAPIView, TagProductsAPIView,
                                   ProductSearchAPIView, DiscountedProductsAPIView, ProductDetailAPIView,
                                   BuyInOneClickAPIView, BasketAddAPIView, BasketAddAnonymousAPIView,
                                   BasketUpdateAPIView, BasketRemoveAPIView,
                                   BasketAnonymousUpdateAPIView, BasketAnonymousRemoveAPIView, ChangeComparisonAPIView,
                                   ComparisonAPIView)
from .views.reviews_views import AddProductReviewAPIView, CreateBlogCommentAPIView
from .views.users_views import UserLoginAPIView, UserRegistrationAPIView, UserProfileAPIView, UserCartAPIView, \
    UserCartRemoveAPIView, UserCartUpdateAPIView, GuestCartAPIView, GuestCartRemoveAPIView, GuestCartUpdateAPIView, \
    SaveDeliveryToSessionAPIView, EmailVerificationAPIView, CreateCallbackQueryAPIView, SubscribeNewsAPIView, \
    ApplyPromoCodeAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'api'


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('base/', BaseAPIView.as_view(), name='base-api'),
    path('index/', IndexAPIView.as_view(), name='index-api'),
    path('comparison/', ComparisonAPIView.as_view(), name='comparison'),
    path('change_comparison/', ChangeComparisonAPIView.as_view(), name='change_comparison'),
    path('catalog/', ProductsListAPIView.as_view(), name='index'),
    path('baskets/add/', BasketAddAPIView.as_view(), name='basket_add'),
    path('baskets/add_anonymous/', BasketAddAnonymousAPIView.as_view(), name='basket_add_anonymous'),
    path('baskets/update/', BasketUpdateAPIView.as_view(), name='basket_update'),
    path('baskets/update_anonymous/', BasketAnonymousUpdateAPIView.as_view(), name='basket_update_anonymous'),
    path('baskets/remove/', BasketRemoveAPIView.as_view(), name='basket_remove'),
    path('baskets/remove_anonymous/', BasketAnonymousRemoveAPIView.as_view(), name='basket_remove_anonymous'),
    path('buy_in_one_click/', BuyInOneClickAPIView.as_view(), name='buy_in_one_click'),
    path('search/', ProductSearchAPIView.as_view(), name='product_search'),
    path('tag/<str:tag_slug>/', TagProductsAPIView.as_view(), name='tag_products'),
    path('discount/', DiscountedProductsAPIView.as_view(), name='discount'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('catalog/<slug:product_slug>/<int:product_id>/', ProductDetailAPIView.as_view(), name='product_detail'),
    path('catalog/<slug:category_slug>/', CategoryProductsListAPIView.as_view(), name='category'),
    path('catalog/<slug:category_slug>/<slug:subcategory_slug>/', SubcategoryProductsListAPIView.as_view(), name='subcategory'),
    path('users/login/', UserLoginAPIView.as_view(), name='user-login-api'),
    path('users/register/', UserRegistrationAPIView.as_view(), name='user-registration-api'),
    path('users/verify/<str:email>/<uuid:code>/', EmailVerificationAPIView.as_view(), name='email_verification'),
    path('users/profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('users/cart/', login_required(UserCartAPIView.as_view()), name='cart'),
    path('users/cart/remove/', login_required(UserCartRemoveAPIView.as_view()), name='cart_remove'),
    path('users/cart/update/', login_required(UserCartUpdateAPIView.as_view()), name='cart_update'),
    path('users/cart_guest/', GuestCartAPIView.as_view(), name='cart_guest'),
    path('users/cart_guest/remove/', GuestCartRemoveAPIView.as_view(), name='cart_guest_remove'),
    path('users/cart_guest/update/', GuestCartUpdateAPIView.as_view(), name='cart_guest_update'),
    path('users/save_delivery/', SaveDeliveryToSessionAPIView.as_view(), name='save_delivery'),
    path('users/callback/', CreateCallbackQueryAPIView.as_view(), name='create-callback-query'),
    path('users/subscribe_news/', SubscribeNewsAPIView.as_view(), name='subscribe_news'),
    path('users/apply_promo_code/', ApplyPromoCodeAPIView.as_view(), name='apply_promo_code'),
    path('blog/', BlogIndexAPIView.as_view(), name='blog_index'),
    path('blog/article/<slug:slug>/', ArticleDetailAPIView.as_view(), name='article_detail'),
    path('blog/<slug:tag_slug>/', TagArticlesListAPIView.as_view(), name='tag_articles'),
    path('blog/category/<slug:category_slug>/', CategoryArticlesListAPIView.as_view(), name='category_articles'),
    path('reviews/add_review/', AddProductReviewAPIView.as_view(), name='add_review'),
    path('reviews/create_comment/', CreateBlogCommentAPIView.as_view(), name='create_comment'),
    path('orders/checkout/', CheckoutAPIView.as_view(), name='checkout'),
    path('orders/<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path('orders/my-list/', OrderListAPIView.as_view(), name='orders_list'),
]