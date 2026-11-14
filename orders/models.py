from django.db import models
from django.contrib.auth.models import User
from accounts.models import Address
from store.models import Product
import uuid


class Order(models.Model):
    PAYMENT_METHODS = (
        ('COD', 'Cash on Delivery'),
        ('UPI', 'UPI / QR Code Scan'),
        ('CARD', 'Credit / Debit Card'),
        ('NETBANKING', 'Internet Banking'),
    )

    PAYMENT_STATUS = (
        ('PENDING', 'Pending'),
        ('PAID', 'Payment Received'),
        ('FAILED', 'Payment Failed'),
    )

    ORDER_STATUS = (
        ('ORDERED', 'Order Placed'),
        ('CONFIRMED', 'Order Confirmed'),
        ('SHIPPED', 'Shipped'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    order_number = models.CharField(max_length=32, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    shipping_address_snapshot = models.TextField(help_text="Snapshot of address at time of order")
    
    total_mrp = models.DecimalField(max_digits=10, decimal_places=2)
    product_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=30, blank=True)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_total = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='COD')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    transaction_id = models.CharField(max_length=64, blank=True)

    order_status = models.CharField(max_length=25, choices=ORDER_STATUS, default='ORDERED')
    tracking_notes = models.JSONField(default=list, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"BZ-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def can_cancel(self):
        return self.order_status in ['ORDERED', 'CONFIRMED']

    @property
    def status_step(self):
        steps = {
            'ORDERED': 1,
            'CONFIRMED': 2,
            'SHIPPED': 3,
            'OUT_FOR_DELIVERY': 4,
            'DELIVERED': 5,
            'CANCELLED': 0,
        }
        return steps.get(self.order_status, 1)

    @property
    def badge_class(self):
        mapping = {
            'ORDERED': 'bg-primary',
            'CONFIRMED': 'bg-info text-dark',
            'SHIPPED': 'bg-warning text-dark',
            'OUT_FOR_DELIVERY': 'bg-secondary',
            'DELIVERED': 'bg-success',
            'CANCELLED': 'bg-danger',
        }
        return mapping.get(self.order_status, 'bg-secondary')

    def __str__(self):
        return f"Order #{self.order_number} ({self.user.username}) - ₹{self.final_total}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    product_title = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=60, blank=True)
    product_image_url = models.URLField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product_title} in #{self.order.order_number}"
