from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.generic import View
from oscauth.models import AuthUserDept
from django.contrib.auth.mixins import PermissionRequiredMixin


class Gcp(PermissionRequiredMixin, View):
    permission_required = 'oscauth.can_order'

    def post(self, request):
        return HttpResponseRedirect('/orders/cart/' + request.POST['deptid'])

    def get(self, request):

        template = loader.get_template('services/gcp.html')
        #template = loader.get_template('/order/cart.html')

        context = {
            'title': 'Order GCP',
        }
        return HttpResponse(template.render(context, request))

