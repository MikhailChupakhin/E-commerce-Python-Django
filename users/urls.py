from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path

from users.views import (EmailVerificationView,
                         FeedbackView, GuestCartRemoveView,
                         GuestCartUpdateView, GuestCartView,
                         SaveDeliveryToSessionView, SubscribeNewsView,
                         SuccessFeedbackView, UserCartRemoveView,
                         UserCartUpdateView, UserCartView, UserLoginView,
                         UserProfileView, UserRigistrationView, ApplyPromoCodeView)

app_name = 'users'


urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('registration/', UserRigistrationView.as_view(), name='registration'),
    path('profile/<int:pk>/', login_required(UserProfileView.as_view()), name='profile'),
    path('cart_guest/', GuestCartView.as_view(), name='cart_guest'),
    path('cart_guest/remove/<int:pk>/', GuestCartRemoveView.as_view(), name='cart_guest_remove'),
    path('cart_guest/update/', GuestCartUpdateView.as_view(), name='cart_guest_update'),
    path('cart/<int:pk>/', login_required(UserCartView.as_view()), name='cart'),
    path('cart/<int:pk>/remove/', UserCartRemoveView.as_view(), name='cart_remove'),
    path('cart/<int:pk>/update/', UserCartUpdateView.as_view(), name='cart_update'),
    path('save_delivery/', SaveDeliveryToSessionView.as_view(), name='save_delivery'),
    path('apply_promo_code/', ApplyPromoCodeView.as_view(), name='apply_promo_code'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify/<str:email>/<uuid:code>/', EmailVerificationView.as_view(), name='email_verification'),
    path('feedback/', FeedbackView.as_view(), name='feedback_view'),
    path('feedback/success/', SuccessFeedbackView.as_view(), name='success_feedback'),
    # path('callback/', CreateCallbackQueryView.as_view(), name='create-callback-query'),
    path('subscribe_news/', SubscribeNewsView.as_view(), name='subscribe_news'),
]