from django.test import TestCase
from django.urls import reverse
from django.test import Client

class CartPageTest(TestCase):
	@classmethod

	def test_cart(self):
		response = self.client.get('/orders/cart/0')
		self.assertEqual(response.status_code, 200)
		print("Cart view works.")

