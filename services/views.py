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


SLUGS = {'midesktop': Pool,
         'midesktop-image': Image,
         'midesktop-network': Network}


def get_instance(service, id):
    model = SLUGS(service)
    instance = get_object_or_404(model, pk=id)
    return instance


def user_has_access(user, owner):
    mc = MCommunity()
    mc.get_group(owner.name)

    if user.username in mc.members:
        return True
    else:
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
            groups = LDAPGroupMember.objects.filter(username=self.request.user).order_by('ldap_group')
            network_groups = list(LDAPGroupMember.objects.filter(username=self.request.user).values_list('ldap_group_id',flat=True))
            networks = Network.objects.filter(status='A',owner__in=network_groups).order_by('name')
            images = Image.objects.filter(status='A',owner__in=network_groups).order_by('name')
            form = MiDesktopNewForm(request.POST, user=self.request.user)

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

            
            if form.is_valid():
                instance = form.save()
                r = create_ticket('New', instance, request, form=form)
                return HttpResponseRedirect('/requestsent')
            else:
                return render(request, 'services/midesktop.html',context)
        elif service == 'midesktop-network':
            form = MiDesktopNewNetworkForm(request.POST, user=self.request.user)
            if form.is_valid():
                instance = form.save()
                r = create_ticket('New', instance, request, form=form)
                return HttpResponseRedirect('/requestsent')
            else:
                print(form.errors)
        elif service == 'midesktop-image':
            
            form = MiDesktopNewImageForm(request.POST, user=self.request.user)
            if form.is_valid():
                instance = form.save()
                multi_disk = request.POST.get('multi_disk')
                disks = multi_disk.split(",")
                num_disks = 0
                for disk in disks:
                    if len(disk) > 0 :
                        new_disk = ImageDisk(
                            image = instance,
                            name = 'disk_' + str(num_disks),
                            size = int(disk)
                        )
                        num_disks += 1
                        new_disk.save()
                r = create_ticket('New', instance, request, form=form)
                return HttpResponseRedirect('/requestsent')
            else:
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
                context["calculator_form"] = CalculatorForm(initial={
                    'multi_disk': '50,'
                })
                return render(request, 'services/midesktop-image.html',context)
        else:
            model = getattr(Service, service)
            form = globals()[service.capitalize() + 'NewForm'](request.POST, user=self.request.user)
            title = f'Request {model._meta.verbose_name.title()} {model.instance_label}'

            if form.is_valid():
                form.save()
                r = create_ticket('New', form.instance, request, title=title)

                if model == Container:
                    return render(request, 'services/new_container.html', {'link': form.instance.project_url, 'title': 'New Container Service Project'})
                else:
                    return HttpResponseRedirect('/requestsent')
            else:
                print(form.errors)

        return render(request, self.template,
                      {'title': form.title,
                       'form': form, })

    def get(self, request, service):
        request.session['backupStorage'] = 'midesktop'
        if service == 'midesktop':
            form = MiDesktopNewForm(user=self.request.user)
            #groups = LDAPGroupMember.objects.filter(username=self.request.user).order_by('ldap_group')
            groups = MCommunity().get_groups_with_id(self.request.user.username)
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
            context["groups_json"] = json.dumps(groups)
            context["network_json"] = json.dumps(network_list)
            context["image_json"] = json.dumps(image_list)

            return render(request, 'services/midesktop.html',context)
        if service == 'midesktop-network':
            form = MiDesktopNewNetworkForm(user=self.request.user)
            return render(request, 'services/midesktop-network.html',{
                'form':form})
        if service == 'midesktop-image':
            form = MiDesktopNewImageForm(user=self.request.user)
            groups = MCommunity().get_groups_with_id(self.request.user.username)
            network_groups = list(LDAPGroupMember.objects.filter(username=self.request.user).values_list('ldap_group_id',flat=True))
            networks = Network.objects.filter(status='A',owner__in=network_groups).order_by('name')
            network_list = []
            for network in networks:
                network_list.append({
                    "id": network.id,
                    "name": network.name,
                    "owner": network.owner_id
                })

            context = {}
            context["form"] = form
            context["groups_json"] = json.dumps(groups)
            context["network_json"] = json.dumps(network_list)
            context["calculator_form"] = CalculatorForm(initial={
                'multi_disk': '50,'
            })

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
        if not self.request.user.is_authenticated:
            return False
        
        service = self.kwargs.get('service')
        id = self.kwargs.get('id')
        self.model = SLUGS.get(service)
        self.instance = get_object_or_404(self.model, pk=id)

        if user_has_access(self.request.user, self.instance.owner):
            return True

    def post(self, request, service, id):
        if service == 'midesktop-network':
            instance = get_object_or_404(Network, pk=id)
            if not user_has_access(request.user, instance.owner):
                return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')
            instance.status = Status.ENDED
            instance.save()
            r = create_ticket('Delete', instance, request)
            return HttpResponseRedirect('/requestsent')
        elif service == 'midesktop-image':
            instance = get_object_or_404(Image, pk=id)
            if not user_has_access(request.user, instance.owner):
                return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')
            instance.status = Status.ENDED
            instance.save()
            r = create_ticket('Delete', instance, request)
            return HttpResponseRedirect('/requestsent')
        elif service == 'midesktop':
            instance = get_object_or_404(Pool, pk=id)
            if not user_has_access(request.user, instance.owner):
                return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')
            instance.status = Status.ENDED
            instance.save()
            r = create_ticket('Delete', instance, request)
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
            request.session['backupStorage'] = 'midesktop'
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
        if not self.request.user.is_authenticated:
            return False
        
        service = self.kwargs.get('service')
        id = self.kwargs.get('id')
        self.model = SLUGS.get(service)
        self.instance = get_object_or_404(self.model, pk=id)

        if user_has_access(self.request.user, self.instance.owner):
            return True

    def post(self, request, service, id):
        if service == 'midesktop-network':
            template = 'services/midesktop-network_change.html'
            instance = Network.objects.get(id=id)
            title = 'Modify ' + instance._meta.verbose_name.title()
            form = MiDesktopChangeNetworkForm(request.POST, user=self.request.user, instance=instance)
            if form.is_valid():
                form.save()
                r = create_ticket('Modify', instance, request, form=form)
                return HttpResponseRedirect('/requestsent')
            return render(request, template,
                        {'title': title,
                        'form': form, })
        elif service == 'midesktop-image':
            template = 'services/midesktop-image_change.html'
            instance = Image.objects.get(id=id)
            title = 'Modify ' + instance._meta.verbose_name.title()
            form = MiDesktopChangeImageForm(request.POST, user=self.request.user,instance = instance)
            if form.is_valid():
                form.save()
                multi_disk = request.POST.get('multi_disk')
                disks = multi_disk.split(",")
                current_disks = ImageDisk.objects.filter(image=instance.id).order_by('name')
                old_disks = list(current_disks.values_list('size', flat=True))
                current_disks.delete()
                num_disks = 0
                for disk in disks:
                    if len(disk) > 0 :
                        new_disk = ImageDisk(
                            image = instance,
                            name = 'disk_' + str(num_disks),
                            size = int(disk)
                        )
                        num_disks += 1
                        new_disk.save()

                r = create_ticket('Modify', instance, request, form=form, old_disks=old_disks, new_disks=disks)
                return HttpResponseRedirect('/requestsent')
            return render(request, template,
                        {'title': title,
                        'form': form, })
        elif service == 'midesktop':
            instance = Pool.objects.get(id=id)
            title = 'Modify ' + instance._meta.verbose_name.title()
            if instance.type == 'instant_clone':
                template = 'services/midesktop-instant-clone_change.html'
                image_name = request.POST['images']
                image = Image.objects.get(name = image_name)
                form = InstantClonePoolChangeForm(request.POST, user = self.request.user, instance = instance, image = image)
            if instance.type == 'persistent':
                template = 'services/midesktop-persistent_change.html'
                form = PersistentPoolChangeForm(request.POST, user = self.request.user, instance = instance)
            if instance.type == 'external':
                template = 'services/midesktop-external_change.html'
                form = ExternalPoolChangeForm(request.POST, user = self.request.user, instance = instance)
            if form.is_valid():
                old_images = list(form.instance.images.all().values_list('name', flat=True))  # Capture this for reference in the ticket.
                form.save()
                r = create_ticket('Modify', instance, request, form=form, old_images=old_images)
                return HttpResponseRedirect('/requestsent')
            else:
                print(form.errors)
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
            if not user_has_access(request.user, instance.owner):
                return HttpResponseNotFound(f'<h1>User { request.user } does not have access to that {instance.instance_label}</h1>')
            
            network_groups = list(LDAPGroupMember.objects.filter(username=self.request.user).values_list('ldap_group_id',flat=True))

            networks = Network.objects.filter(status='A',owner__in=network_groups).order_by('name')
            network_list = []
            for network in networks:
                network_list.append({
                    "id": network.id,
                    "name": network.name,
                    "owner": network.owner_id
                })
            # Fetch disks related to the instance
            disks = ImageDisk.objects.filter(image=instance.id).order_by('name')

            # Prepare initial data for the formset
            disk_data = [{'size': disk.size} for disk in disks]
            multi_disk_string = ''
            for disk in disk_data:
                multi_disk_string = multi_disk_string + str(disk['size']) + ','

            calculator_form = CalculatorForm(initial={
                'cpu': instance.cpu,
                'memory': instance.memory,
                'gpu': instance.gpu,
                'multi_disk': multi_disk_string
            })
            title = 'Modify ' + instance._meta.verbose_name.title()
            form = MiDesktopChangeImageForm(user=self.request.user, instance=instance)
            return render(request, template,
                        {'title': title,
                        'form': form,
                        'calculator_form': calculator_form,
                        'network_json': json.dumps(network_list)},
                        )
        elif service == 'midesktop':
            instance = get_object_or_404(Pool,pk=id, status=Status.ACTIVE)
            title = 'Modify ' + instance._meta.verbose_name.title()
            if instance.type == 'instant_clone':
                template = 'services/midesktop-instant-clone_change.html'
                image = instance.images.all()[0]
                if instance.override:
                    cpu =instance.cpu_override
                    memory = instance.memory_override
                    cpu_rate = image.cpu_rate()
                    memory_rate = image.memory_rate()
                    total_cost_without_cpu_and_memory = image.total_cost_without_cpu_and_memory()
                    image.total_cost = total_cost_without_cpu_and_memory + (cpu * cpu_rate) + (memory * memory_rate)
                form = InstantClonePoolChangeForm(user=self.request.user, instance=instance,  image=image)
                return render(request, template,
                        {'title': title,
                        'form': form,})

            if instance.type == 'persistent':
                template = 'services/midesktop-persistent_change.html'
                pool_images = instance.images.all()
                form = PersistentPoolChangeForm(user=self.request.user, instance=instance)
                images = Image.objects.filter(status='A',owner__in=[instance.owner.id]).order_by('name')
                current_images = instance.images.all()
                current_image_list = []
                for image in current_images:
                    current_image_list.append({
                        "id": image.id,
                        "name": image.name,
                        "owner": instance.owner.id,
                        "total_cost": json.dumps(image.total_cost, default=float)
                    })
                image_list = []
                for image in images:
                    image_list.append({
                        "id": image.id,
                        "name": image.name,
                        "owner": instance.owner.id,
                        "total_cost": json.dumps(image.total_cost, default=float)
                    })
                image_json = json.dumps(image_list)
                current_images_json = json.dumps(current_image_list)

                return render(request, template,
                        {'title': title,
                        'form': form,
                        'image_json': image_json,
                        'pool_images': pool_images,
                        'current_images_json': current_images_json})
            if instance.type == 'external':
                template = 'services/midesktop-external_change.html'
                form = ExternalPoolChangeForm(user=self.request.user, instance=instance)
                return render(request, template,{'title':title,'form': form,})
            
            

        else:
            request.session['backupStorage'] = 'midesktop'
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
            request.session['backupStorage'] = 'midesktop'
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
