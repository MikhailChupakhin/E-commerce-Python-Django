from django.contrib import admin

from products.admin import BasketAdmin
from users.models import CallbackQuery, EmailVerification, Feedback, User
from .models import PromoCode
from .models import Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username',)
    inlines = (BasketAdmin,)


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'expiration')
    fields = ('code', 'user', 'expiration', 'created')
    readonly_fields = ('created',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'name', 'email', 'phone')
    fields = ('created_at', 'message', 'name', 'email', 'phone')
    readonly_fields = ('created_at',)

@admin.register(CallbackQuery)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'name', 'phone')
    fields = ('created_at', 'name', 'phone')
    readonly_fields = ('created_at',)

admin.site.register(Subscription)


class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'start_date', 'end_date', 'max_uses', 'current_uses')
    list_filter = ('start_date', 'end_date')
    search_fields = ('code',)

admin.site.register(PromoCode, PromoCodeAdmin)

