from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Product, Order

class StoreTests(TestCase):
    def setUp(self):
        Product.objects.create(name='Test Item', price=10.00)

    def test_product_list(self):
        c = Client()
        resp = c.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Test Item')

    def test_checkout_requires_login(self):
        c = Client()
        c.get('/cart/add/1/')
        resp = c.get('/checkout/')
        # redirects to login if not authenticated
        self.assertEqual(resp.status_code, 302)

    def test_checkout_flow(self):
        user = User.objects.create_user('alice', 'a@example.com', 'pass1234')
        c = Client()
        c.login(username='alice', password='pass1234')
        c.get('/cart/add/1/')
        resp = c.get('/checkout/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Order.objects.filter(user=user).exists())
