from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.generic import View
from oscauth.models import AuthUserDept
from django.contrib.auth.mixins import UserPassesTestMixin



class ServicesView(UserPassesTestMixin, View):

    def test_func(self):

        if self.request.user.is_authenticated:
            return True
        else:
            return False


class Gcp(ServicesView):

    def post(self, request):
        return HttpResponseRedirect('/orders/cart/' + request.POST['deptid'])

    def get(self, request):

        template = loader.get_template('services/gcp.html')
        #template = loader.get_template('/order/cart.html')

        context = {
            'title': 'Order GCP',
        }
        return HttpResponse(template.render(context, request))


class Aws(ServicesView):

    def post(self, request):
        return HttpResponseRedirect('/orders/cart/' + request.POST['deptid'])

    def get(self, request):

        template = loader.get_template('services/gcp.html')
        #template = loader.get_template('/order/cart.html')

        context = {
            'title': 'Order Amazon Web Services',
        }
        return HttpResponse(template.render(context, request))


class Azure(ServicesView):

    def post(self, request):
        return HttpResponseRedirect('/orders/cart/' + request.POST['deptid'])

    def get(self, request):

        template = loader.get_template('services/gcp.html')
        #template = loader.get_template('/order/cart.html')

        context = {
            'title': 'Order Azure',
        }
        return HttpResponse(template.render(context, request))