from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from decimal import Decimal


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cart_items')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_entries')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def subtotal(self):
        return self.product.selling_price * self.quantity

    @property
    def mrp_subtotal(self):
        return self.product.mrp_price * self.quantity

    @property
    def savings(self):
        return self.mrp_subtotal - self.subtotal

    def __str__(self):
        return f"{self.quantity}x {self.product.title}"


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_entries')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"


class Coupon(models.Model):
    DISCOUNT_TYPES = (
        ('PERCENT', 'Percentage (%)'),
        ('FIXED', 'Fixed Amount (₹)'),
    )

    code = models.CharField(max_length=30, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, default='PERCENT')
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    def calculate_discount(self, total_amount):
        if total_amount < self.min_purchase:
            return Decimal('0.00')

        if self.discount_type == 'PERCENT':
            discount = (total_amount * self.discount_value) / Decimal('100.00')
            if self.max_discount and discount > self.max_discount:
                discount = self.max_discount
            return round(discount, 2)
        else:
            return min(self.discount_value, total_amount)

    def __str__(self):
        return f"{self.code} ({self.discount_value}{'%' if self.discount_type == 'PERCENT' else ' ₹'} off)"
