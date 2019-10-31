from django.test import TestCase
from django.urls import reverse
from django.test import Client
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

test_url_list = ['/','/help','/auth/get_uniqname/','/auth/mypriv/','/contact','/orders/services/']
c = Client()
c.post('/admin/login/',{'next': 'admin','username': 'testuser', 'password': 'check123'})
for url in test_url_list:
    print("Testing " +  url)
    response = c.get(url)
    print(response.status_code)
    if (response.status_code != 200):
        print("FAIL")
    else:
        print("PASS")
    assert response.status_code == 200