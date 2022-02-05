from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.generic import View
from oscauth.models import AuthUserDept
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import AwsNewForm
from project.integrations import create_ticket



class ServicesView(UserPassesTestMixin, View):

    def test_func(self):

        if self.request.user.is_authenticated:
            return True
        else:
            return False


class Gcp(ServicesView):

    def post(self, request):
        print('post GCP')
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
        print('post AWS', request.POST)

        create_ticket('ADD', 'AWS', request.POST)


        return HttpResponseRedirect('/services/aws/')

    def get(self, request):

        template = loader.get_template('services/aws.html')
        #template = loader.get_template('/order/cart.html')
        form = AwsNewForm()

        context = {
            'title': 'Order Amazon Web Services',
            'form': form
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