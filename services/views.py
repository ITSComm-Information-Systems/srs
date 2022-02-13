from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.template import loader
from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import AwsNewForm
from .models import *
from project.integrations import create_ticket


class ServicesView(UserPassesTestMixin, View):

    def test_func(self):

        if self.request.user.is_authenticated:
            return True
        else:
            return False


def change_request(request, service, id):
    if hasattr(Service, service):
        model = getattr(Service, service)
        request.session['backupStorage'] = 'cloud'
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    instance = get_object_or_404(model, pk=id)

    return render(request, f'services/{service}_change.html', 
            {'title': f'Modify {model.instance_label} Request',
             'instance': instance,
            })


def get_service_list(request, service):
    if hasattr(Service, service):
        model = getattr(Service, service)
        request.session['backupStorage'] = 'cloud'
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    service_list = model.objects.filter(status='A')

    return render(request, 'services/service_list.html', 
            {'title': model._meta.verbose_name_plural,
             'service_list': service_list,
            })
    #return HttpResponse(template.render(context, request))

class Gcp(ServicesView):

    def post(self, request):
        print('post GCP')
        return HttpResponseRedirect('/orders/cart/' + request.POST['deptid'])

    def get(self, request):
        request.session['backupStorage'] = 'cloud'
        template = loader.get_template('services/gcp.html')
        #template = loader.get_template('/order/cart.html')

        context = {
            'title': 'Order GCP',
        }
        return HttpResponse(template.render(context, request))


class Aws(ServicesView):
    template = 'services/aws.html'

    def post(self, request):
        print('post AWS', request.POST)

        form = AwsNewForm(request.POST)

        if form.is_valid():
            print('valid')
            form.save()
        else:
            print('not valid form')
            for err in form.errors:
                print(err)

        #create_ticket('ADD', 'AWS', request.POST)

        return render(request, self.template,
                      {'title': 'Order Amazon Web Services',
                       'form': form, })



    def get(self, request):
        request.session['backupStorage'] = 'cloud'

        #template = loader.get_template('/order/cart.html')
        form = AwsNewForm()

        return render(request, self.template,
                      {'title': 'Order Amazon Web Services',
                       'form': form, })


class Azure(ServicesView):

    def post(self, request):
        return HttpResponseRedirect('/orders/cart/' + request.POST['deptid'])

    def get(self, request):
        request.session['backupStorage'] = 'cloud'
        template = loader.get_template('services/gcp.html')
        #template = loader.get_template('/order/cart.html')

        context = {
            'title': 'Order Azure',
        }
        return HttpResponse(template.render(context, request))