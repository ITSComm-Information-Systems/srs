from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.template import loader
from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import *
from .models import *
from project.integrations import create_ticket, Openshift, TDx
from oscauth.models import LDAPGroupMember
import json


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
        if service == 'midesktop':
            form = MiDesktopNewForm(request.POST, user=self.request.user)
            print('bing bong')
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/requestsent')
            else:
                print(form.errors)
        elif service == 'midesktop-network':
            form = MiDesktopNewNetworkForm(request.POST, user=self.request.user)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/requestsent')
            else:
                print(form.errors)
        elif service == 'midesktop-image':
            form = MiDesktopNewImageForm(request.POST, user=self.request.user)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/requestsent')
            else:
                print(form.errors)
        else:
            model = getattr(Service, service)
            form = globals()[service.capitalize() + 'NewForm'](request.POST, user=self.request.user)
            title = f'Request {model._meta.verbose_name.title()} {model.instance_label}'

            if form.is_valid():
                form.save()
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
        if service == 'midesktop':
            form = MiDesktopNewForm(user=self.request.user)
            groups = LDAPGroupMember.objects.filter(username=self.request.user).order_by('ldap_group')
            network_groups = list(LDAPGroupMember.objects.filter(username=self.request.user).values_list('ldap_group_id',flat=True))
            networks = Network.objects.filter(status='A',owner__in=network_groups).order_by('name')
            images = Image.objects.filter(status='A',owner__in=network_groups).order_by('name')
            network_list = []
            for network in networks:
                network_list.append({
                    "id": network.id,
                    "name": network.name,
                    "owner": network.owner_id
                })
            
            group_list = []
            for group in groups:
                group_list.append({'name':group.ldap_group.name,'id':group.ldap_group_id})

            image_list = []
            for image in images:
                image_list.append({
                    
                    "id": image.id,
                    "name": image.name,
                    "owner": image.owner_id,
                    "total_cost":str(image.total_cost)
                
                })

            context = {}
            context["form"] = form
            context["groups_json"] = json.dumps(group_list)
            context["network_json"] = json.dumps(network_list)
            context["image_json"] = json.dumps(image_list)

            return render(request, 'services/midesktop.html',context)
        if service == 'midesktop-network':
            form = MiDesktopNewNetworkForm(user=self.request.user)
            return render(request, 'services/midesktop-network.html',{
                'form':form})
        if service == 'midesktop-image':
            form = MiDesktopNewImageForm(user=self.request.user)
            #groups = MCommunity().get_groups(self.request.user.username)
            groups = LDAPGroupMember.objects.filter(username=self.request.user).order_by('ldap_group')
            network_groups = list(LDAPGroupMember.objects.filter(username=self.request.user).values_list('ldap_group_id',flat=True))
            networks = Network.objects.filter(status='A',owner__in=network_groups).order_by('name')
            network_list = []
            for network in networks:
                network_list.append({
                    "id": network.id,
                    "name": network.name,
                    "owner": network.owner_id
                })
            
            group_list = []
            for group in groups:
                group_list.append({'name':group.ldap_group.name,'id':group.ldap_group_id})

            context = {}
            context["form"] = form
            context["groups_json"] = json.dumps(group_list)
            context["network_json"] = json.dumps(network_list)

            return render(request, 'services/midesktop-image.html',context)
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
        if service == 'midesktop-network':
            instance = get_object_or_404(Network, pk=id)
            if not user_has_access(request.user, instance.owner):
                return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')
            instance.status = Status.ENDED
            instance.save()
            return HttpResponseRedirect('/requestsent')
        elif service == 'midesktop-image':
            instance = get_object_or_404(Image, pk=id)
            if not user_has_access(request.user, instance.owner):
                return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')
            instance.status = Status.ENDED
            instance.save()
            return HttpResponseRedirect('/requestsent')
        elif service == 'midesktop':
            instance = get_object_or_404(Pool, pk=id)
            if not user_has_access(request.user, instance.owner):
                return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')
            instance.status = Status.ENDED
            instance.save()
            return HttpResponseRedirect('/requestsent')
        else:

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
        if service == 'midesktop-network':
            #template = 'services/midesktop-network_delete.html'
            instance = get_object_or_404(Network, pk=id)
            if not user_has_access(request.user, instance.owner):
                return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')
            return render(request, self.template,
                        {
                        'instance': instance, })
        elif service == 'midesktop-image':
            instance = get_object_or_404(Image, pk=id)
            if not user_has_access(request.user, instance.owner):
                return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')
            return render(request, self.template,
                        {
                        'instance': instance, })
        elif service == 'midesktop':
            instance = get_object_or_404(Pool, pk=id)
            if not user_has_access(request.user, instance.owner):
                return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')
            return render(request, self.template,
                        {
                        'instance': instance, })
        else:
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
        if service == 'midesktop-network':
            template = 'services/midesktop-network_change.html'
            instance = Network.objects.get(id=id)
            title = 'Modify ' + instance._meta.verbose_name.title()
            form = MiDesktopChangeNetworkForm(request.POST, user=self.request.user, instance=instance)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/requestsent')
            return render(request, template,
                        {'title': title,
                        'form': form, })
        elif service == 'midesktop-image':
            template = 'services/midesktop-image_change.html'
            instance = Image.objects.get(id=id)
            image_form = ImageForm(initial={'name':instance.name})
            title = 'Modify ' + instance._meta.verbose_name.title()
            form = MiDesktopChangeImageForm(request.POST, user=self.request.user,instance = instance)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/requestsent')
            return render(request, template,
                        {'title': title,
                        'form': form, })

        else:
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
        if service == 'midesktop-network':
            template = 'services/midesktop-network_change.html'
            instance = get_object_or_404(Network,pk=id, status=Status.ACTIVE)
            if not user_has_access(request.user, instance.owner):
                return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')
            title = 'Modify ' + instance._meta.verbose_name.title()
            form = MiDesktopChangeNetworkForm(user=self.request.user, instance=instance)
            return render(request, template,
                        {'title': title,
                        'form': form, })
        elif service =='midesktop-image':
            template = 'services/midesktop-image_change.html'
            instance = get_object_or_404(Image,pk=id, status=Status.ACTIVE)
            calculator_form = CalculatorForm(initial={'cpu':instance.cpu,'memory':instance.memory,'gpu':instance.gpu,})
            image_form = ImageForm(initial={'name':instance.name})
            if not user_has_access(request.user, instance.owner):
                return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')
            title = 'Modify ' + instance._meta.verbose_name.title()
            form = MiDesktopChangeImageForm(user=self.request.user, instance=instance)
            return render(request, template,
                        {'title': title,
                        'form': form,
                        'calculator_form': calculator_form,
                        'image_form':image_form })
        elif service == 'midesktop':
            template = 'services/midesktop-instant-clone_change.html'
            instance = get_object_or_404(Pool,pk=id, status=Status.ACTIVE)
            image = instance.images.all()[0]
            images = Image.objects.filter(status='A',owner__in=[instance.owner.id]).order_by('name')
            title = 'Modify ' + instance._meta.verbose_name.title()
            form = InstantClonePoolChangeForm(user=self.request.user, instance=instance, image=image)
            return render(request, template,
                        {'title': title,
                        'form': form,})

        else:
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

            return render(request, self.template,
                        {'title': title,
                        'form': form, })


def get_service_list(request, service):
    groups = list(LDAPGroupMember.objects.filter(username=request.user).values_list('ldap_group_id',flat=True))
    if service == 'midesktop':
        template = 'services/midesktop_existing.html'
        pool_list = Pool.objects.filter(status='A',owner__in=groups).order_by('name')
        return render(request,template,{
                'pool_list': pool_list,
                'groups': groups,})
    elif service == 'midesktop-image':
        image_list = Image.objects.filter(status='A',owner__in=groups).order_by('name')
        return render(request,'services/midesktop-image_existing.html',{'groups': groups,'image_list':image_list})
    elif service == 'midesktop-network':
        template = 'services/midesktop-network_existing.html'
        service_list = Network.objects.filter(status='A',owner__in=groups).order_by('name')
        return render(request,template,{
                'service_list': service_list,
                'groups': groups,})
    else:
        if hasattr(Service, service):
            model = getattr(Service, service)
            request.session['backupStorage'] = 'cloud'
        else:
            return HttpResponseNotFound('<h1>Page not found</h1>')

        

        if service == 'gcp':
            template = 'gcp_service_list.html'
            service_list = GCPAccount.objects.filter(status='A',owner__in=groups).order_by('account_id')
        else:
            template = 'service_list.html'
            service_list = model.objects.filter(status='A',owner__in=groups)

        return render(request, f'services/{template}', 
                {'title': model._meta.verbose_name_plural,
                'instance_label': model.instance_label,
                'service_list': service_list,
                'groups': groups,
                })
