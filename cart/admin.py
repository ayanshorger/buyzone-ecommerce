from django.contrib import admin
from .models import CartItem, WishlistItem, Coupon


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'session_key', 'quantity', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__title', 'user__username', 'session_key')


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'created_at')
    search_fields = ('product__title', 'user__username')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_purchase', 'max_discount', 'is_active')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code',)
