from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.template import loader
from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import *
from .models import *
from project.integrations import create_ticket, Openshift, TDx, create_midesktop_ticket
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

        if service == "clouddesktop":
            self.template = 'services/add_cloud_desktop.html'
            title = 'MiDesktop New Order'

        if form.is_valid():
            form.save()
            if service == "clouddesktop":
                r = create_midesktop_ticket('New', form.instance, request,form, title=title)
            else:
                r = create_ticket('New', form.instance, request, title=title)

            if model == Container:
                project_url = f'{Openshift.PROJECT_URL}/{form.instance.project_name}'
                return render(request, 'services/new_container.html', {'link': project_url, 'title': 'New Container Service Project'})
            else:
                return HttpResponseRedirect('/requestsent')
        else:
            print(form.errors)

        return render(request, self.template,
                      {'title': form.title,
                       'form': form, })

    def get(self, request, service):
        request.session['backupStorage'] = 'cloud'
        if service == "clouddesktop":
            self.template = 'services/add_cloud_desktop.html'

        try:
            form = globals()[service.capitalize() + 'NewForm'](user=self.request.user)
        except KeyError:
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

        instance.status = Status.ENDED
        instance.save()

        create_ticket('Delete', instance, request, title=f'Delete {instance._meta.verbose_name.title()}') # {model.instance_label}
        

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

class ImageDeleteView(UserPassesTestMixin, View):
    template = 'services/image_delete.html'

    def test_func(self):
        if self.request.user.is_authenticated:
            return True
        else:
            return False
        
    def get(self, request, service, id):
        model = CloudImage.objects.filter(status='A').order_by('account_id')
        instance = get_object_or_404(model, pk=id)
        title = f'Delete {instance._meta.verbose_name.title()}'

        if not user_has_access(request.user, instance.owner):
            return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')

        return render(request, self.template,
                      {'title': title,
                       'instance': instance, })
    
    def post(self, request, service, id):

        if request.POST.get('confirm_delete') != 'on':
            return HttpResponseRedirect(request.path) 

        if request.POST.get('instance') != str(id):
            return HttpResponseRedirect(request.path) 
        
        model = CloudImage.objects.filter(status='A').order_by('account_id')
        instance = get_object_or_404(model, pk=id)

        if not user_has_access(request.user, instance.owner):
            return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')
        
        instance.status = Status.ENDED
        instance.save()
        
        create_ticket('Delete', instance, request, title=f'Delete {instance._meta.verbose_name.title()}') # {model.instance_label}
        return HttpResponseRedirect('/requestsent')
        
class ImageChangeView(UserPassesTestMixin, View):
    template = 'services/image_change.html'
    
    def test_func(self):
        if self.request.user.is_authenticated:
            return True
        else:
            return False
        
    def post(self, request, service, id):
        model = CloudImage.objects.filter(status='A').order_by('account_id')
        instance = get_object_or_404(model, pk=id)      
        
        form = ClouddesktopImageChangeForm(request.POST, user=self.request.user, instance=instance)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect('/requestsent')
        else:
            return render(request, self.template,
                {'form': form, })

        
        
    def get(self, request, service, id):
        model =  CloudImage.objects.filter(status='A').order_by('account_id')
        instance = get_object_or_404(model, pk=id)

        if not user_has_access(request.user, instance.owner):
            return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')

        form = ClouddesktopImageChangeForm(user=self.request.user, instance=instance)
        return render(request, self.template,
                      {'form': form, })


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
            if not service == 'gcpaccount':
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
        except KeyError:
            return HttpResponseNotFound('<h1>Page not found</h1>')
        
        if service == 'clouddesktop':
            self.template = 'services/pool_change.html'
            image = CloudImage.objects.filter(id=instance.image_id).first()
            shared = False
            if instance.shared_network:
                shared = True


            return render(request, self.template,
                      {'title': title,
                       'form': form,
                       'image': image,
                       'shared': shared})

        return render(request, self.template,
                      {'title': title,
                       'form': form, })


def get_service_list(request, service):
    groups = list(LDAPGroupMember.objects.filter(username=request.user).values_list('ldap_group_id',flat=True))
    if hasattr(Service, service):
        if service == 'clouddesktop':
            pools = CloudDesktop.objects.filter(status='A',owner__in=groups).order_by('account_id')
            images = CloudImage.objects.filter(status='A',owner__in=groups).order_by('account_id')
        else:
            model = getattr(Service, service)
            request.session['backupStorage'] = 'cloud'
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    

    if service == 'gcp':
        template = 'gcp_service_list.html'
        service_list = GCPAccount.objects.filter(status='A',owner__in=groups).order_by('account_id')
    elif service == 'clouddesktop':
        template = 'services/clouddesktop_service_list.html'
        return render(request, template,{
                      'title':'Test Title',
                      'instance_label': 'pools',
                      'pools': pools,
                      'images': images,
                      'groups': groups
        })
    else:
        template = 'service_list.html'
        service_list = model.objects.filter(status='A',owner__in=groups)

    return render(request, f'services/{template}', 
            {'title': model._meta.verbose_name_plural,
             'instance_label': model.instance_label,
             'service_list': service_list,
             'groups': groups,
            })

