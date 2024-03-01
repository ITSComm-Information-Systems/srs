from django.test import TestCase
from services.models import Network, Image, Pool
from django.test import Client
from django.contrib.auth.models import User

# TestCase required method names: setUp, test_*, tearDown

def login_as_user(username):
    c = Client()
    c.force_login(User.objects.get(username=username), backend='django.contrib.auth.backends.ModelBackend')
    return c

class MiDesktop(TestCase):
    def setUp(self):
        self.client = login_as_user('djamison')

    def verify_redirect(self, descr, data, url):  # POST, verify no form errors, verify redirect.
        response = self.client.post(url, data)

        if 'form' in response.context:
            errors = response.context["form"].errors
            self.assertEqual(len(errors), 0, f'{descr} : {errors}')

        self.assertEqual(response.status_code, 302, descr)

    def test_pools(self):
        test = 'New Instant Clone Pool, New Image, New Network'
        data = {'admin_group': ['ITSComm Information Systems'], 'shortcode': ['940314'], 'pool_name': ['dj-pool-instant'], 'pool_accessibility': ['From UMNet Only'], 'pool_type': ['instant_clone'], 'auto_logout': ['Never'], 'ad_container': [''], 'base_image': ['999999999'], 'image_name': ['dj-bass-image'], 'initial_image': ['Standard'], 'operating_system': ['Windows10 64bit'], 'cpu': ['1'], 'cpu_cost': ['1.15'], 'memory': ['2'], 'memory_cost': ['1.92'], 'disk-TOTAL_FORMS': ['2'], 'disk-INITIAL_FORMS': ['0'], 'disk-MIN_NUM_FORMS': ['0'], 'disk-MAX_NUM_FORMS': ['1000'], 'disk-0-size': ['50'], 'disk-0-cost': ['5.00'], 'disk-1-size': ['100'], 'disk-1-cost': ['10.00'], 'storage_cost': ['15.00'], 'multi_disk': ['50,100,'], 'gpu': ['True'], 'gpu_cost': ['6.07'], 'total': ['55.45'], 'pool_quantity': ['1'], 'pool_total': ['55.45'], 'network_type': ['dedicated'], 'network': ['new'], 'network_name': ['dj-net-32'], 'access_internet': ['True'], 'mask': ['32'], 'protection': ['datacenter'], 'technical_contact': ['djamison@umich.edu'], 'business_contact': ['rhoffer@umich.edu'], 'security_contact': ['jwalfish@umich.edu'], 'additional_details': [test], 'sla': ['on']}
        self.verify_redirect(test, data, "/services/midesktop/add/")
        network = Network.objects.get(name='dj-net-32')

        test = 'New Persistent Pool, New image, Shared Network (Web-Access)'
        data = {'admin_group': ['ITSComm Information Systems'], 'shortcode': ['940314'], 'pool_name': ['dj-pool-persistent'], 'pool_accessibility': ['Publicly Available'], 'pool_type': ['persistent'], 'auto_logout': ['Never'], 'ad_container': [''], 'base_image': ['999999999'], 'image_name': ['dj-image-large'], 'initial_image': ['Blank'], 'operating_system': ['Windows11 64bit'], 'cpu': ['2'], 'cpu_cost': ['2.30'], 'memory': ['4'], 'memory_cost': ['3.84'], 'disk-TOTAL_FORMS': ['1'], 'disk-INITIAL_FORMS': ['0'], 'disk-MIN_NUM_FORMS': ['0'], 'disk-MAX_NUM_FORMS': ['1000'], 'disk-0-size': ['50'], 'disk-0-cost': ['5.00'], 'storage_cost': ['5.00'], 'multi_disk': ['50,'], 'gpu': ['True'], 'gpu_cost': ['6.07'], 'total': ['48.52'], 'pool_quantity': ['1'], 'pool_total': ['48.52'], 'network_type': ['web-access'], 'network_name': [''], 'access_internet': ['True'], 'mask': ['16'], 'protection': ['datacenter'], 'technical_contact': [''], 'business_contact': [''], 'security_contact': [''], 'additional_details': [test], 'sla': ['on']}
        self.verify_redirect(test, data, "/services/midesktop/add/")
        large_image = Image.objects.get(name='dj-image-large')

        test = 'New Instant Clone Pool, reuse image+network.'
        bass_image = Image.objects.get(name='dj-bass-image')
        data = {'admin_group': ['ITSComm Information Systems'], 'shortcode': ['940314'], 'pool_name': ['dj-pool-reuse-image'], 'pool_accessibility': ['No Restriction'], 'pool_type': ['instant_clone'], 'auto_logout': ['Never'], 'ad_container': [''], 'base_image': [bass_image.id], 'image_name': [''], 'initial_image': ['Blank'], 'operating_system': ['Windows10 64bit'], 'cpu': ['1'], 'cpu_cost': ['1.15'], 'memory': ['2'], 'memory_cost': ['1.92'], 'disk-TOTAL_FORMS': ['1'], 'disk-INITIAL_FORMS': ['0'], 'disk-MIN_NUM_FORMS': ['0'], 'disk-MAX_NUM_FORMS': ['1000'], 'disk-0-size': ['50'], 'disk-0-cost': ['5.00'], 'storage_cost': ['5.00'], 'multi_disk': ['50,'], 'gpu': ['False'], 'gpu_cost': ['0.00'], 'total': ['39.38'], 'pool_quantity': ['25'], 'pool_total': ['1362.25'], 'network_name': [''], 'access_internet': ['True'], 'mask': ['16'], 'protection': ['datacenter'], 'technical_contact': [''], 'business_contact': [''], 'security_contact': [''], 'additional_details': [test], 'sla': ['on']}
        self.verify_redirect(test, data, "/services/midesktop/add/")

        test = 'New external pool'
        data = {'admin_group': ['ITSComm Information Systems'], 'shortcode': ['940314'], 'pool_name': ['dj-pool-external'], 'pool_accessibility': ['No Restriction'], 'pool_type': ['external'], 'auto_logout': ['Never'], 'ad_container': [''], 'image_name': [''], 'initial_image': ['Blank'], 'operating_system': ['Windows10 64bit'], 'cpu': ['1'], 'cpu_cost': ['1.15'], 'memory': ['2'], 'memory_cost': ['0.96'], 'disk-TOTAL_FORMS': ['1'], 'disk-INITIAL_FORMS': ['0'], 'disk-MIN_NUM_FORMS': ['0'], 'disk-MAX_NUM_FORMS': ['1000'], 'disk-0-size': ['50'], 'disk-0-cost': ['5.0'], 'storage_cost': ['5.0'], 'multi_disk': [''], 'gpu': ['False'], 'gpu_cost': ['0.0'], 'total': ['38.42'], 'pool_quantity': ['10'], 'pool_total': ['100.00'], 'network_name': [''], 'access_internet': ['True'], 'mask': ['16'], 'protection': ['datacenter'], 'technical_contact': [''], 'business_contact': [''], 'security_contact': [''], 'additional_details': [test], 'sla': ['on']}
        self.verify_redirect(test, data, "/services/midesktop/add/")
        
        response = self.client.get("/services/midesktop/")
        self.assertEqual(response.status_code, 200, 'View all Desktops')

        test = 'Change dj-pool-external quantity to 20.'
        data = {'shortcode': ['940314'], 'quantity': ['20'], 'total': ['200.00'], 'additional_details': [test]}
        pool = Pool.objects.get(name='dj-pool-external')
        self.verify_redirect(test, data, f"/services/midesktop/{pool.id}/change/")

        test = 'Change dj-pool-instant image from dj-bass-image to dj-image-large and quantity from 1 to 5.'
        data = {'shortcode': ['940314'], 'images': ['dj-image-large'], 'quantity': ['5'], 'total': ['272.45'], 'additional_details': [test]}
        pool = Pool.objects.get(name='dj-pool-instant')
        self.verify_redirect(test, data, f"/services/midesktop/{pool.id}/change/")

        response = self.client.get(f"/services/midesktop/{pool.id}/delete/")
        self.assertEqual(response.status_code, 200, 'Display Delete page')
        
        test = 'delete dj-pool-instant'
        data = {'instance': [pool.id], 'confirm_delete': ['on']}
        self.verify_redirect(test, data, f"/services/midesktop/{pool.id}/delete/")

        test = 'Modify dj-pool-persistent add dj-bass-image'
        data = {'shortcode': ['940314'], 'multi_image': ['', f'{large_image.id},{bass_image.id}'], 'total': ['101.09'], 'additional_details': [test]}
        pool = Pool.objects.get(name='dj-pool-persistent')
        self.verify_redirect(test, data, f"/services/midesktop/{pool.id}/change/")

    def test_images(self):
        test = 'New Image, New Network (dj-network-break)'
        data = {'admin_group': ['ITSComm Information Systems'], 'name': ['dj-newimage-newnetwork'], 'initial_image': ['Standard'], 'operating_system': ['Windows 11 64bit'], 'cpu': ['1'], 'cpu_cost': ['1.15'], 'memory': ['2'], 'memory_cost': ['0.96'], 'disk-TOTAL_FORMS': ['1'], 'disk-INITIAL_FORMS': ['0'], 'disk-MIN_NUM_FORMS': ['0'], 'disk-MAX_NUM_FORMS': ['1000'], 'disk-0-size': ['50'], 'disk-0-cost': ['5.00'], 'storage_cost': ['5.00'], 'multi_disk': ['50,'], 'gpu': ['False'], 'gpu_cost': ['0.00'], 'total': ['38.42'], 
                'network_type': ['dedicated'], 'network': ['new'], 'network_name': ['dj-network-break'], 'access_internet': ['True'], 'mask': ['256'], 'protection': ['none'], 'technical_contact': ['djamison@umich.edu'], 'business_contact': ['djamison@umich.edu'], 'security_contact': ['djamison@umich.edu']}
        self.verify_redirect(test, data, '/services/midesktop-image/add/')

        test = 'New Image, Existing Dedicated Network'
        network = Network.objects.get(name='dj-network-break')
        data = {'admin_group': ['ITSComm Information Systems'], 'name': ['dj-just-image'], 'initial_image': ['Standard'], 'operating_system': ['Windows 11 64bit'], 'cpu': ['1'], 'cpu_cost': ['1.15'], 'memory': ['4'], 'memory_cost': ['1.92'], 'disk-TOTAL_FORMS': ['2'], 'disk-INITIAL_FORMS': ['0'], 'disk-MIN_NUM_FORMS': ['0'], 'disk-MAX_NUM_FORMS': ['1000'], 'disk-0-size': ['50'], 'disk-0-cost': ['5.00'], 'disk-1-size': ['100'], 'disk-1-cost': ['10.00'], 'storage_cost': ['15.00'], 'multi_disk': ['50,100,'], 'gpu': ['True'], 'gpu_cost': ['6.07'], 'total': ['55.45'], 
                'network_type': ['dedicated'], 'network': [network.id], 'network_name': [''], 'access_internet': ['True'], 'mask': ['16'], 'protection': ['datacenter'], 'technical_contact': [''], 'business_contact': [''], 'security_contact': ['']}
        self.verify_redirect(test, data, '/services/midesktop-image/add/')

        test = 'New Image, Private Network'
        data = {'admin_group': ['ITSComm Information Systems'], 'name': ['dj-newimage-privatenet'], 'initial_image': ['Blank'], 'operating_system': ['Windows10 64bit'], 'cpu': ['1'], 'cpu_cost': ['1.15'], 'memory': ['2'], 'memory_cost': ['0.96'], 'disk-TOTAL_FORMS': ['1'], 'disk-INITIAL_FORMS': ['0'], 'disk-MIN_NUM_FORMS': ['0'], 'disk-MAX_NUM_FORMS': ['1000'], 'disk-0-size': ['50'], 'disk-0-cost': ['5.00'], 'storage_cost': ['5.00'], 'multi_disk': ['50,'], 'gpu': ['False'], 'gpu_cost': ['0.00'], 'total': ['38.42'], 
                'network_type': ['private'], 'network_name': [''], 'access_internet': ['True'], 'mask': ['16'], 'protection': ['datacenter'], 'technical_contact': [''], 'business_contact': [''], 'security_contact': ['']}
        self.verify_redirect(test, data, '/services/midesktop-image/add/') 

    def test_networks(self):
        data = {'admin_group': ['ITSComm Information Systems'], 'purpose': ['Flipper'], 'access_internet': ['True'], 'mask': ['16'], 'dhcp': ['true'], 'protection': ['datacenter'], 'technical_contact': ['djamison@umich.edu'], 'business_contact': ['djamison@umich.edu'], 'security_contact': ['djamison@umich.edu']}
        response = self.client.post("/services/midesktop-network/add/", data)
        self.assertEqual(response.status_code, 302)

        response = self.client.get("/services/midesktop-network/", data)  # View all networks
        self.assertEqual(response.status_code, 200)