from django.test import TestCase
from django.urls import reverse
from django.test import Client
import django

class CartPageTest(TestCase):

    @classmethod
    def setUpClass(cls):
        #creating instance of a client.
        super(CartPageTest, cls).setUpClass() 
        django.setup()
        #self.client = Client()

    def test(self):
        print("Running test for View.")
        c = Client()
        response = c.get('/')
        self.assertEqual(response.status_code, 200)
        print(response.status_code)

    '''def test_cart(self):
        print("Running test for Cart View.")
        c = Client()
        c.post('/admin/login/', {'next': 'admin','username': 'admin', 'password': 'magpie'})
        c.post('/auth/su_login/',{'user': '1653','submit': 'Change Login'}, content_type='application/json')
        response = c.get('/orders/cart/0')
        #self.assertEqual(response.status_code, 200)
        print(response.status_code)
        print("Cart View Page Works.")

    def test_order(self):
        print("Running test for Order View.")
        c = Client()
        c.post('/admin/login/', {'next': 'admin','username': 'admin', 'password': 'magpie'})
        c.post('/auth/su_login/',{'user': '1653','submit': 'Change Login'}, content_type='application/json')
        response = c.get('/orders/status/0')
        #self.assertEqual(response.status_code, 200)
        print(response.status_code)
        print("Order View Page Works.")'''

    def test_help(self):
        print("Running test for Help View.")
        c = Client()
        c.post('/admin/login/',{'next': 'admin','username': 'admin', 'password': 'magpie'})
        response = c.get('/help')
        self.assertEqual(response.status_code, 200)
        print(response.status_code)
        print("Help Page Works.")

    def test_request_services(self):
        print("Running test for Requesting Services")
        c = Client()
        c.post('/admin/login/',{'next': 'admin','username': 'admin', 'password': 'magpie'})
        response = c.get('/orders/services/')
        self.assertEqual(response.status_code, 200)
        print(response.status_code)
        print("Requesting Services Page Works.")

    def test_manage_user_access(self):
        print("Running test for Manage User Access")
        c = Client()
        c.post('/admin/login/',{'next': 'admin','username': 'admin', 'password': 'magpie'})
        response = c.get('/auth/get_uniqname/')
        self.assertEqual(response.status_code, 200)
        print(response.status_code)
        print("Manage User Access Page Works.")


