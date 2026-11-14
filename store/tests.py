from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from store.models import Category, Product, Review
from cart.models import CartItem, Coupon
from decimal import Decimal


class BuyzoneStoreTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testshopper', password='password123')
        self.category = Category.objects.create(name='Smartphones', slug='smartphones')
        self.product = Product.objects.create(
            title='Test Phone X',
            slug='test-phone-x',
            brand='TestBrand',
            category=self.category,
            sku='TEST-SKU-001',
            description='A fantastic test phone with 5G connectivity.',
            mrp_price=Decimal('50000.00'),
            selling_price=Decimal('40000.00'),
            stock=15,
            is_available=True,
            rating=4.5,
            num_reviews=1
        )
        self.coupon = Coupon.objects.create(
            code='SAVE10',
            discount_type='PERCENT',
            discount_value=Decimal('10.00'),
            min_purchase=Decimal('1000.00'),
            is_active=True
        )

    def test_home_page_status(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Buyzone')

    def test_product_list_and_search(self):
        # List
        response = self.client.get(reverse('store:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Phone X')

        # Search matching
        search_resp = self.client.get(reverse('store:product_list') + '?q=Phone')
        self.assertEqual(search_resp.status_code, 200)
        self.assertContains(search_resp, 'Test Phone X')

        # Search not matching
        nomatch_resp = self.client.get(reverse('store:product_list') + '?q=NonexistentDevice')
        self.assertContains(nomatch_resp, 'No Products Found')

    def test_product_detail(self):
        response = self.client.get(reverse('store:product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Phone X')
        self.assertContains(response, 'TEST-SKU-001')
        self.assertEqual(self.product.discount_percentage, 20)

    def test_cart_add_and_view(self):
        self.client.login(username='testshopper', password='password123')
        # Add to cart
        resp = self.client.post(reverse('cart:add_to_cart', kwargs={'product_id': self.product.id}), {'quantity': 2})
        self.assertEqual(resp.status_code, 302)

        # Verify in cart
        cart_resp = self.client.get(reverse('cart:cart_view'))
        self.assertEqual(cart_resp.status_code, 200)
        self.assertContains(cart_resp, 'Test Phone X')
        self.assertContains(cart_resp, '₹80,000')

    def test_coupon_discount_calculation(self):
        discount = self.coupon.calculate_discount(Decimal('10000.00'))
        self.assertEqual(discount, Decimal('1000.00'))

    def test_pincode_check_endpoint(self):
        resp = self.client.get(reverse('store:check_pincode') + '?pincode=560103')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('FREE Delivery', data['message'])
