from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from store.models import Category, Product
from accounts.models import Address
from cart.models import CartItem
from orders.models import Order
from decimal import Decimal


class BuyzoneOrderTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='ordershopper', password='password123')
        self.client.login(username='ordershopper', password='password123')

        self.address = Address.objects.create(
            user=self.user,
            full_name='Test Shopper',
            phone='9876543210',
            street_address='100 Innovation Road',
            city='Bengaluru',
            state='Karnataka',
            postal_code='560001',
            is_default=True
        )

        self.category = Category.objects.create(name='Laptops', slug='laptops')
        self.product = Product.objects.create(
            title='Pro Laptop 14',
            slug='pro-laptop-14',
            brand='TechBrand',
            category=self.category,
            sku='TECH-LAP-14',
            description='Powerful 14-inch laptop for developers.',
            mrp_price=Decimal('100000.00'),
            selling_price=Decimal('90000.00'),
            stock=10,
            is_available=True
        )

    def test_complete_checkout_flow(self):
        # 1. Add item to cart
        self.client.post(reverse('cart:add_to_cart', kwargs={'product_id': self.product.id}), {'quantity': 1})
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 1)

        # 2. Get checkout page
        checkout_page = self.client.get(reverse('orders:checkout'))
        self.assertEqual(checkout_page.status_code, 200)

        # 3. Post checkout form
        post_data = {
            'selected_address_id': self.address.id,
            'payment_method': 'UPI',
            'upi_id': 'test@okaxis',
        }
        response = self.client.post(reverse('orders:checkout'), post_data)
        self.assertEqual(response.status_code, 302)

        # 4. Verify order created
        order = Order.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.final_total, Decimal('90000.00'))
        self.assertEqual(order.payment_method, 'UPI')
        self.assertEqual(order.payment_status, 'PAID')
        self.assertEqual(order.items.count(), 1)

        # 5. Verify stock decremented (was 10, now 9)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 9)

        # 6. Verify cart was cleared
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 0)

        # 7. Verify order detail page and visual tracking status
        detail_resp = self.client.get(reverse('orders:order_detail', kwargs={'order_number': order.order_number}))
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, order.order_number)
        self.assertContains(detail_resp, 'Confirmed')

        # 8. Test Order Cancellation
        cancel_resp = self.client.get(reverse('orders:cancel_order', kwargs={'order_number': order.order_number}))
        self.assertEqual(cancel_resp.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.order_status, 'CANCELLED')

        # Verify stock was restored to 10
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)
