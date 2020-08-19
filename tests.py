# Did not test Apps (need to check form urls and permissions)
import django, os, sys, copy, unittest, subprocess
from django.test import SimpleTestCase
from django.urls import reverse
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

#Keep below django setup
from order.models import Action
from pages.models import Page
from django.contrib.auth.models import User

start = subprocess.check_output("python manage.py show_urls", shell=True, stderr=subprocess.STDOUT).decode(sys.stdout.encoding) # Use for OpenShift
# start=os.popen("py manage.py show_urls").read() # Use for local

everything=str(start)
codes={100: [], 101: [], 102: [], 200: [], 201: [], 202: [], 203: [], 204: [], 205: [], 206: [], 207: [], 208: [], 226: [], 300: [], 301: [], 302: [], 303: [], 304: [], 305: [], 307: [], 308: [], 400: [], 401: [], 402: [], 403: [], 404: [], 405: [], 406: [], 407: [], 408: [], 409: [], 410: [], 411: [], 412: [], 413: [], 414: [], 415: [], 416: [], 417: [], 418: [], 421: [], 422: [], 423: [], 424: [], 426: [], 428: [], 429: [], 431: [], 444: [], 451: [], 499: [], 500: [], 501: [], 502: [], 503: [], 504: [], 505: [], 506: [], 507: [], 508: [], 510: [], 511: [], 599: [], 'error':[]}

# get urls from django-extensions result
onlyurls=[]
urls=everything.split('\n')
for tup in urls:
    group=tup.split()
    if len(group)!=0:
        onlyurls.append(group[0])

exclude=['__debug__', 'download','<', 'admin', 'su_login', 'oidc', 'auth/su', 'logout', 'ajax','pages']

storage={}
for url in onlyurls:
    if not any(ele in url for ele in exclude):
        section=url[1:].split('/')[0]
        storage[section]=storage.get(section,[])
        storage[section].append(url)

# General use login
c = Client()
c.force_login(User.objects.get(username='admin'))
#actual testing
class TestStatic(unittest.TestCase):    
    def test_page_error(self):
        #customloginhere
        results=copy.deepcopy(codes)
        pages=list(Page.objects.all().values_list('permalink', flat=True))
        exceptions=['/notices/1','/links/2','/notice/3','/links/1','/notices/2']
        for url in pages:
            if not any(ele in url for ele in exceptions):
                try:
                    results[c.get(url).status_code].append(url)
                except:
                    results['error'].append(url)
        self.assertEqual(results['error'], [])
        self.assertEqual(results[404], [])
        print('Not tested in Pages:')
        print([e for e in exceptions])
    
    def test_wf_error(self):
        #customloginhere
        results=copy.deepcopy(codes)
        workflows=list(Action.objects.all().values_list('id', flat=True))
        exceptions=[]
        for i in workflows:
            url="/orders/wf/"+str(i)
            try:
                results[c.get(url).status_code].append(url)
            except:
                results['error'].append(url)
        self.assertEqual(results['error'], [])
        self.assertEqual(results[404], [])
        print('Not tested in Workflows:')
        print([e for e in exceptions])
        
class TestOther(unittest.TestCase):
    # 1. Need to add roles and permissions in order to test, otherwise everything is 403.
    # 2. How to possibly add:
    # perm = Permission.objects.get(codename='can_approve_requests')
    # user.user_permissions.add(perm)
    # 3. Currently does not distinguish between rte/bom/mbid (use as reference only, rewrite later)
    # def test_apps(self):
    #     #customloginhere
    #     results=copy.deepcopy(codes)
    #     exceptions=['/apps/rte/view-time/display/','/apps/rte/update/get-update-entries/']
    #     for url in storage['apps']:
    #         if not any(ele in url for ele in exceptions):
    #             try:
    #                 results[c.get(url).status_code].append(url)
    #             except:
    #                 results['error'].append(url)
    #     self.assertEqual(results['error'], [])
    #     self.assertEqual(results[404], [])
    #     print('Not tested:')
    #     print([e for e in exceptions])

    def test_auth(self):
        #customloginhere
        results=copy.deepcopy(codes)
        exceptions=['/auth/adduser/', '/auth/get_dept/', '/auth/modpriv/', '/auth/showpriv/']
        for url in storage['auth']:
            if not any(ele in url for ele in exceptions):
                try:
                    results[c.get(url).status_code].append(url)
                except:
                    results['error'].append(url)
        self.assertEqual(results['error'], [])
        self.assertEqual(results[404], [])
        print('Not tested in Auth:')
        print([e for e in exceptions])

    def test_chartchange(self):
        #customloginhere
        results=copy.deepcopy(codes)
        exceptions=[]
        for url in storage['chartchange']:
            if not any(ele in url for ele in exceptions):
                try:
                    results[c.get(url).status_code].append(url)
                except:
                    results['error'].append(url)
        self.assertEqual(results['error'], [])
        self.assertEqual(results[404], [])
        print('Not tested in Chartchange:')
        print([e for e in exceptions])
 
    def test_orders(self):
        #customloginhere
        results=copy.deepcopy(codes)
        exceptions=['/orders/sendemail/','/orders/addtocart/','/orders/cart/','/orders/chartcom/', '/orders/deletefromcart/','/orders/review','/orders/submit']
        for url in storage['orders']:
            if not any(ele in url for ele in exceptions):
                try:
                    results[c.get(url).status_code].append(url)
                except:
                    results['error'].append(url)
        self.assertEqual(results['error'], [])
        self.assertEqual(results[404], [])
        print('Not tested in Orders:')
        print([e for e in exceptions])
    
    def test_reports(self):
        #customloginhere
        # needs to add permission 'oscauth.can_report'
        results=copy.deepcopy(codes)
        exceptions=['/reports/doc/report/', '/reports/doc/report/detail/', '/reports/doc/select-cf/', '/reports/inventory/report', '/reports/nonteleph/report/', '/reports/soc/report', '/reports/tolls/']
        for url in storage['reports']:
            if not any(ele in url for ele in exceptions):
                try:
                    results[c.get(url).status_code].append(url)
                except:
                    results['error'].append(url)
        self.assertEqual(results['error'], [])
        self.assertEqual(results[404], [])
        print('Not tested in Reports:')
        print([e for e in exceptions])
    
    def test_tools(self):
        #customloginhere
        results=copy.deepcopy(codes)
        exceptions=['/tools/voip/confirm/']
        for url in storage['tools']:
            if not any(ele in url for ele in exceptions):
                try:
                    results[c.get(url).status_code].append(url)
                except:
                    results['error'].append(url)
        self.assertEqual(results['error'], [])
        self.assertEqual(results[404], [])
        print('Not tested in Tools:')
        print([e for e in exceptions])
    
    def test_other(self):
        #customloginhere
        results=copy.deepcopy(codes)
        exceptions=[]
        for key in list(storage.keys()):
            if key not in ['','api','apps','auth','chartchange','orders','reports','tools']:
                for url in storage[key]:
                    try:
                        results[c.get(url).status_code].append(url)
                    except:
                        results['error'].append(url)
        self.assertEqual(results['error'], [])
        self.assertEqual(results[404], [])
        print('Not tested in anything else:')
        print([e for e in exceptions])

# Run to print all url results
# Update exclusion lists as needed
# Urls that Forms POST to should be excluded

exclude=['__debug__', 'download','<', 'admin', 'su_login', 'oidc', 'auth/su', 'logout', 'ajax', 'pages']
pageExceptions=['/notices/1','/links/2','/notice/3','/links/1','/notices/2']
appsExceptions=['/apps/rte/view-time/display/','/apps/rte/update/get-update-entries/']
authExceptions=['/auth/adduser/', '/auth/get_dept/', '/auth/modpriv/', '/auth/showpriv/']
ordersExceptions=['/orders/sendemail/','/orders/addtocart/','/orders/cart/','/orders/chartcom/', '/orders/deletefromcart/']
reportsExceptions=['/reports/doc/report/', '/reports/doc/report/detail/', '/reports/doc/select-cf/', '/reports/inventory/report', '/reports/nonteleph/report/', '/reports/soc/report', '/reports/tolls/']
toolsExceptions=['/tools/voip/confirm/']

sections=[pageExceptions,appsExceptions,authExceptions,ordersExceptions,reportsExceptions,toolsExceptions]
for s in sections:
    exclude.extend(s)

clean=set()
for url in onlyurls:
    if not any(ele in url for ele in exclude):
        clean.add(url)

workflows=list(Action.objects.all().values_list('id', flat=True))
pages=list(Page.objects.all().values_list('permalink', flat=True))
main_code=copy.deepcopy(codes)
wf_code=copy.deepcopy(codes)
page_code=copy.deepcopy(codes)

#actual testing

c = Client()
c.force_login(User.objects.get(username='admin'))

for url in pages:
    if not any(ele in url for ele in exclude):
        try:
            page_code[c.get(url).status_code].append(url)
        except:
            page_code['error'].append(url)
        
for i in workflows:
    url="/orders/wf/"+str(i)
    if not any(ele in url for ele in exclude):
        try:
            wf_code[c.get(url).status_code].append(url)
        except:
            wf_code['error'].append(url)

for url in clean:
    if not any(ele in url for ele in exclude):
        try:
            main_code[c.get(url).status_code].append(url)
        except:
            main_code['error'].append(url)

print("Excluding:")
for item in exclude:
    print(item)
print('Results of testing urls in Pages')
for key, val in page_code.items():
    if val!=[]:
        print()
        print(str(key)+" results:")
        for url in val:
            print(url)
print('Results of testing urls in Workflows')
for key, val in wf_code.items():
    if val!=[]:
        print()
        print(str(key)+" results:")
        for url in val:
            print(url)
print('Results of testing urls found overall')
for key, val in main_code.items():
    if val!=[]:
        print()
        print(str(key)+" results:")
        for url in val:
            print(url)