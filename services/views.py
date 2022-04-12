from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.template import loader
from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import *
from .models import *
from project.integrations import create_ticket
from oscauth.models import LDAPGroupMember


def user_has_access(user, owner):
    try:
        x = LDAPGroupMember.objects.get(username=user.username, ldap_group_id=owner.id)
        return True
    except:
        return False


class ServiceRequestView(UserPassesTestMixin, View):
    template = 'services/add.html'

    def test_func(self):
        if self.request.user.is_authenticated:
            return True
        else:
            return False

    def post(self, request, service):
        model = getattr(Service, service)
        form = globals()[service.capitalize() + 'NewForm'](request.POST, user=self.request.user)
        title = f'Request {model._meta.verbose_name.title()} {model.instance_label}'

        if form.is_valid():
            form.save()
            instance = model.objects.get(id=form.instance.id)
            create_ticket('New', instance, request, title=title)
            return HttpResponseRedirect('/requestsent')

        return render(request, self.template,
                      {'title': form.title,
                       'form': form, })

    def get(self, request, service):
        request.session['backupStorage'] = 'cloud'

        try:
            form = globals()[service.capitalize() + 'NewForm'](user=self.request.user)
        except:
            return HttpResponseNotFound('<h1>Page not found</h1>')

        return render(request, self.template,
                      {'title': form.title,
                       'form': form, })


class ServiceDeleteView(UserPassesTestMixin, View):
    template = 'services/delete.html'

    def test_func(self):
        if self.request.user.is_authenticated:
            return True
        else:
            return False

    def post(self, request, service, id):

        if request.POST.get('confirm_delete') != 'on':
            return HttpResponseRedirect(request.path) 

        if request.POST.get('instance') != str(id):
            return HttpResponseRedirect(request.path) 

        model = getattr(Service, service)
        instance = get_object_or_404(model, pk=id)

        if not user_has_access(request.user, instance.owner):
            return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')

        create_ticket('Delete', instance, request, title=f'Delete {instance._meta.verbose_name.title()}') # {model.instance_label}
        instance.status = Status.ENDED
        instance.save()

        return HttpResponseRedirect('/requestsent')

    def get(self, request, service, id):
        request.session['backupStorage'] = 'cloud'
        model = getattr(Service, service)
        instance = get_object_or_404(model, pk=id)
        title = f'Delete {instance._meta.verbose_name.title()}'

        if not user_has_access(request.user, instance.owner):
            return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')

        return render(request, self.template,
                      {'title': title,
                       'instance': instance, })


class ServiceChangeView(UserPassesTestMixin, View):
    template = 'services/change.html'

    def test_func(self):
        if self.request.user.is_authenticated:
            return True
        else:
            return False

    def post(self, request, service, id):
        model = getattr(Service, service)
        instance = model.objects.get(id=id)        
        
        form = globals()[service.capitalize() + 'ChangeForm'](request.POST, user=self.request.user, instance=instance)

        if form.is_valid():
            form.save()
            create_ticket('Modify', instance, request, title=f'Modify {instance._meta.verbose_name.title()} {model.instance_label}')
            return HttpResponseRedirect('/requestsent')

        return render(request, self.template,
                      {'title': f'Modify {instance._meta.verbose_name.title()}',
                       'form': form, })

    def get(self, request, service, id):
        request.session['backupStorage'] = 'cloud'
        model = getattr(Service, service)
        instance = get_object_or_404(model, pk=id, status=Status.ACTIVE)

        if not user_has_access(request.user, instance.owner):
            return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')

        title = 'Modify ' + instance._meta.verbose_name.title()

        try:
            form = globals()[service.capitalize() + 'ChangeForm'](user=self.request.user, instance=instance)
        except:
            return HttpResponseNotFound('<h1>Page not found</h1>')

        return render(request, self.template,
                      {'title': title,
                       'form': form, })


def get_service_list(request, service):
    if hasattr(Service, service):
        model = getattr(Service, service)
        request.session['backupStorage'] = 'cloud'
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    groups = list(LDAPGroupMember.objects.filter(username=request.user).values_list('ldap_group_id'))
    service_list = model.objects.filter(status='A',owner__in=groups)

    return render(request, 'services/service_list.html', 
            {'title': model._meta.verbose_name_plural,
             'service_list': service_list,
            })





    