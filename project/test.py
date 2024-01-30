from django.test import TestCase
from services.models import Network, Image, Pool
from django.test import Client
from django.contrib.auth.models import User

# TestCase required method names: setUp, test_*, tearDown

def login_as_user(username):
    c = Client()
    c.force_login(User.objects.get(username='testymac'), backend='django.contrib.auth.backends.ModelBackend')

    # TODO call change_user directly
    user = User.objects.get(username=username)
    response = c.post("/auth/su_login/", {'user': [user.id], 'submit': ['Change Login']})
    print('su', response.status_code)

    return c


class NewNetwork(TestCase):
    def setUp(self):
        pass

    def test_create_network(self):
        print('create network')

        c = login_as_user('djamison')

        data = {'admin_group': ['ITSComm Information Systems'], 'name': ['dj-network'], 'access_internet': ['True'], 'mask': ['64'], 'dhcp': ['true'], 'protection': ['datacenter'], 'technical_contact': ['djamison@umich.edu'], 'business_contact': ['djamison@umich.edu'], 'security_contact': ['djamison@umich.edu']}
        response = c.post("/services/midesktop-network/add/", data)
        self.assertEqual(response.status_code, 302)

        net = Network.objects.get(name="dj-network")
        self.assertEqual(net.name, 'dj-network')
        print('end create')

class NewPool(TestCase):

    def test_create_everything(self):
        c = login_as_user('djamison')

        # New Pool, New Image, New Network
        # dj-pool-allnew, dj-bass-image, dj-newnet32
        new_everything = {'admin_group': ['ITSComm Information Systems'], 'shortcode': ['940479'], 'pool_name': ['dj-pool-allnew'], 'pool_type': ['instant_clone'], 'auto_logout': ['Never'], 'ad_container': ['1'], 'base_image': ['999999999'], 'image_name': ['dj-bass-image'], 'initial_image': ['Blank'], 'operating_system': ['Windows10 64bit'], 'cpu': ['1'], 'cpu_cost': ['1.15'], 'memory': ['2'], 'memory_cost': ['1.92'], 'disk-TOTAL_FORMS': ['1'], 'disk-INITIAL_FORMS': ['0'], 'disk-MIN_NUM_FORMS': ['0'], 'disk-MAX_NUM_FORMS': ['1000'], 'disk-0-size': ['50'], 'disk-0-cost': ['5.00'], 'storage_cost': ['5.00'], 'multi_disk': ['50,'], 'gpu': ['False'], 'gpu_cost': ['0.00'], 'total': ['39.38'], 'pool_quantity': ['10'], 'pool_total': ['393.80'], 'network_type': ['dedicated'], 'network': ['new'], 'network_name': ['dj-newnet32'], 'access_internet': ['True'], 'mask': ['32'], 'protection': ['datacenter'], 'technical_contact': ['djamison@umich.edu'], 'business_contact': ['djamison@umich.edu'], 'security_contact': ['djamison@umich.edu'], 'additional_details': ['dj extra'], 'sla': ['on']}
        response = c.post("/services/midesktop/add/", new_everything)
        self.assertEqual(response.status_code, 302)
        dj_newnet32 = Network.objects.get(name='dj-newnet32')
        # 'network_type': ['dedicated'], 'network': ['new'], 'network_name': ['dj-newnet32']

        # New Pool, New Image, Shared Web Access Network
        new_image = {'admin_group': ['ITSComm Information Systems'], 'shortcode': ['940479'], 'pool_name': ['dj-newimage'], 'pool_type': ['instant_clone'], 'auto_logout': ['Never'], 'ad_container': [''], 'base_image': ['999999999'], 'image_name': ['dj-base-10'], 'initial_image': ['Blank'], 'operating_system': ['Windows11 64bit'], 'cpu': ['1'], 'cpu_cost': ['1.15'], 'memory': ['2'], 'memory_cost': ['1.92'], 'disk-TOTAL_FORMS': ['1'], 'disk-INITIAL_FORMS': ['0'], 'disk-MIN_NUM_FORMS': ['0'], 'disk-MAX_NUM_FORMS': ['1000'], 'disk-0-size': ['50'], 'disk-0-cost': ['5.00'], 'storage_cost': ['5.00'], 'multi_disk': ['50,'], 'gpu': ['True'], 'gpu_cost': ['6.07'], 'total': ['45.45'], 'pool_quantity': ['20'], 'pool_total': ['909.00'], 'network_type': ['web-access'], 'network_name': [''], 'access_internet': ['True'], 'mask': ['16'], 'protection': ['datacenter'], 'technical_contact': [''], 'business_contact': [''], 'security_contact': [''], 'additional_details': ['shared web access'], 'sla': ['on']}
        response = c.post("/services/midesktop/add/", new_image)
        self.assertEqual(response.status_code, 302)
        # 'network_type': ['web-access'], 'network_name': [''], 'access_internet': ['True'],

        # New Pool, New Image, Existing Dedicated
        new_image_existing_network = {'admin_group': ['ITSComm Information Systems'], 'shortcode': ['940479'], 'pool_name': ['dj-pool-new-image-existingnetwork'], 'pool_type': ['instant_clone'], 'auto_logout': ['Never'], 'ad_container': [''], 'base_image': ['999999999'], 'image_name': ['dj-base-2'], 'initial_image': ['Blank'], 'operating_system': ['Windows10 64bit'], 'cpu': ['1'], 'cpu_cost': ['1.15'], 'memory': ['2'], 'memory_cost': ['1.92'], 'disk-TOTAL_FORMS': ['1'], 'disk-INITIAL_FORMS': ['0'], 'disk-MIN_NUM_FORMS': ['0'], 'disk-MAX_NUM_FORMS': ['1000'], 'disk-0-size': ['50'], 'disk-0-cost': ['5.00'], 'storage_cost': ['5.00'], 'multi_disk': ['50,'], 'gpu': ['False'], 'gpu_cost': ['0.00'], 'total': ['39.38'], 'pool_quantity': ['1'], 'pool_total': ['39.38'], 'network_type': ['dedicated'], 'network': [dj_newnet32.id], 'network_name': [''], 'access_internet': ['True'], 'mask': ['16'], 'protection': ['datacenter'], 'technical_contact': [''], 'business_contact': [''], 'security_contact': [''], 'additional_details': ['New pool, new image, existing network'], 'sla': ['on']}
        response = c.post("/services/midesktop/add/", new_image_existing_network)
        self.assertEqual(response.status_code, 302)
        dj_base_2_image = Image.objects.get(name='dj-base-2')
        self.assertEqual(dj_base_2_image.memory, 2)

        # 'network_type': ['dedicated'], 'network': ['566'], 'network_name': ['']

        # New Pool, Existing Image
        new_pool = {'admin_group': ['ITSComm Information Systems'], 'shortcode': ['940479'], 'pool_name': ['dj-pool-reuse-image'], 'pool_type': ['instant_clone'], 'auto_logout': ['Never'], 'ad_container': ['1'], 'base_image': [dj_base_2_image.id], 'image_name': [''], 'initial_image': ['Blank'], 'operating_system': ['Windows10 64bit'], 'cpu': ['1'], 'cpu_cost': ['1.15'], 'memory': ['2'], 'memory_cost': ['1.92'], 'disk-TOTAL_FORMS': ['1'], 'disk-INITIAL_FORMS': ['0'], 'disk-MIN_NUM_FORMS': ['0'], 'disk-MAX_NUM_FORMS': ['1000'], 'disk-0-size': ['50'], 'disk-0-cost': ['5.00'], 'storage_cost': ['5.00'], 'multi_disk': ['50,'], 'gpu': ['False'], 'gpu_cost': ['0.00'], 'total': ['39.38'], 'pool_quantity': ['25'], 'pool_total': ['1112.25'], 'network_name': [''], 'access_internet': ['True'], 'mask': ['16'], 'protection': ['datacenter'], 'technical_contact': [''], 'business_contact': [''], 'security_contact': [''], 'additional_details': ['New Pool, existing image.'], 'sla': ['on']}
        response = c.post("/services/midesktop/add/", new_pool)
        self.assertEqual(response.status_code, 302)
        # No Network Data

        # New Image, Existing Dedicated Network (dj-newnet32)
        data = {'admin_group': ['ITSComm Information Systems'], 'name': ['dj-just-image'], 'initial_image': ['Standard'], 'operating_system': ['Windows 11 64bit'], 'cpu': ['1'], 'cpu_cost': ['1.15'], 'memory': ['4'], 'memory_cost': ['1.92'], 'disk-TOTAL_FORMS': ['2'], 'disk-INITIAL_FORMS': ['0'], 'disk-MIN_NUM_FORMS': ['0'], 'disk-MAX_NUM_FORMS': ['1000'], 'disk-0-size': ['50'], 'disk-0-cost': ['5.00'], 'disk-1-size': ['100'], 'disk-1-cost': ['10.00'], 'storage_cost': ['15.00'], 'multi_disk': ['50,100,'], 'gpu': ['True'], 'gpu_cost': ['6.07'], 'total': ['55.45'], 'network_type': ['dedicated'], 'network': [dj_newnet32.id], 'network_name': [''], 'access_internet': ['True'], 'mask': ['16'], 'protection': ['datacenter'], 'technical_contact': [''], 'business_contact': [''], 'security_contact': ['']}
        response = c.post("/services/midesktop-image/add/", data)
        self.assertEqual(response.status_code, 302)
        # 'network_type': ['dedicated'], 'network': ['566'], 'network_name': ['']

        # New Image, Private Network
        data = {'admin_group': ['ITSComm Information Systems'], 'name': ['dj-newimage-privatenet'], 'initial_image': ['Blank'], 'operating_system': ['Windows10 64bit'], 'cpu': ['1'], 'cpu_cost': ['1.15'], 'memory': ['2'], 'memory_cost': ['0.96'], 'disk-TOTAL_FORMS': ['1'], 'disk-INITIAL_FORMS': ['0'], 'disk-MIN_NUM_FORMS': ['0'], 'disk-MAX_NUM_FORMS': ['1000'], 'disk-0-size': ['50'], 'disk-0-cost': ['5.00'], 'storage_cost': ['5.00'], 'multi_disk': ['50,'], 'gpu': ['False'], 'gpu_cost': ['0.00'], 'total': ['38.42'], 'network_type': ['private'], 'network_name': [''], 'access_internet': ['True'], 'mask': ['16'], 'protection': ['datacenter'], 'technical_contact': [''], 'business_contact': [''], 'security_contact': ['']}
        response = c.post("/services/midesktop-image/add/", data)
        self.assertEqual(response.status_code, 302)
        # 'network_type': ['private'], 'network_name': [''],

        # New Image, New Network (dj-network-break)
        data = {'admin_group': ['ITSComm Information Systems'], 'name': ['dj-newimage-newnetwork'], 'initial_image': ['Standard'], 'operating_system': ['Windows 11 64bit'], 'cpu': ['1'], 'cpu_cost': ['1.15'], 'memory': ['2'], 'memory_cost': ['0.96'], 'disk-TOTAL_FORMS': ['1'], 'disk-INITIAL_FORMS': ['0'], 'disk-MIN_NUM_FORMS': ['0'], 'disk-MAX_NUM_FORMS': ['1000'], 'disk-0-size': ['50'], 'disk-0-cost': ['5.00'], 'storage_cost': ['5.00'], 'multi_disk': ['50,'], 'gpu': ['False'], 'gpu_cost': ['0.00'], 'total': ['38.42'], 'network_type': ['dedicated'], 'network': ['new'], 'network_name': ['dj-network-break'], 'access_internet': ['True'], 'mask': ['256'], 'protection': ['none'], 'technical_contact': ['djamison@umich.edu'], 'business_contact': ['djamison@umich.edu'], 'security_contact': ['djamison@umich.edu']}
        response = c.post("/services/midesktop-image/add/", data)
        self.assertEqual(response.status_code, 302)
        # 'network_type': ['dedicated'], 'network': ['new'], 'network_name': ['dj-network-break'], 