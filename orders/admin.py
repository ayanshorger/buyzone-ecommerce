from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_title', 'product_sku', 'price', 'quantity', 'total_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'final_total', 'payment_method', 'payment_status', 'order_status', 'created_at')
    list_filter = ('order_status', 'payment_method', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__username', 'shipping_address_snapshot')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_title', 'price', 'quantity', 'total_price')
    search_fields = ('order__order_number', 'product_title', 'product_sku')
