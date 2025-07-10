from rest_framework import serializers

from project.models import Choice
from services.models import Pool, Image, Network, ImageDisk
from order.models import StorageInstance, ArcInstance, StorageRate, BackupDomain, BackupNode, ArcBilling, BackupDomain, Server, Database, ServerDisk, Ticket, ServerTicket
from oscauth.models import LDAPGroup, LDAPGroupMember
from django.db import models

class ServerDiskSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServerDisk
        fields = ['name', 'size', 'controller', 'device']


class ServerTicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServerTicket
        fields = ['ticket_id', 'comments']


class ImageDiskSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageDisk
        fields = ['name', 'size']

class ChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Choice
        exclude = ['sequence']


def serializer_factory(model):
    name = model.__name__

    meta_attrs = {
        'model': model,
        'fields': '__all__'
    }
    meta = type('Meta', (), meta_attrs)
    class_attrs = {'Meta': meta}
    class_attrs['select_related'] = []
    class_attrs['prefetch_related'] = []

    for fld in model._meta.get_fields():
        if type(fld) == models.fields.related.ForeignKey:
            if fld.related_model == Choice:
                class_attrs[fld.name] = ChoiceSerializer()
            else:
                class_attrs[fld.name] = serializers.StringRelatedField()
            class_attrs['select_related'].append(fld.name)
        elif type(fld) == models.fields.related.ManyToManyField:
            if fld.related_model == Choice:
                class_attrs[fld.name] = ChoiceSerializer(many=True)
            else:
                class_attrs[fld.name] = serializers.StringRelatedField(many=True)
            class_attrs['prefetch_related'].append(fld.name)
                

    if model == Server:   #TODO handle children
        class_attrs['disks'] = ServerDiskSerializer(many=True, read_only=True)
        class_attrs['prefetch_related'].append('disks')
        class_attrs['tickets'] = ServerTicketSerializer(many=True, read_only=True)
        class_attrs['prefetch_related'].append('tickets')
    elif model == Image:
        class_attrs['storage'] = ImageDiskSerializer(many=True, read_only=True)

    return type(f'{name}Serializer', (serializers.ModelSerializer,), class_attrs)

class DatabaseSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ['id']
        model = Database


class StorageRateSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['id','name','label', 'display_seq_no','type','rate','unit_of_measure','service']
        model = StorageRate


class RateSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['name','label','rate']
        read_only_fields = ['name', 'label', 'rate']
        model = StorageRate

class BackupDomainNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackupNode
        fields = ['name']
        
class BackupDomainSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    nodes = serializers.SlugRelatedField(many=True, slug_field='name',read_only=True)
    nodes = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = BackupDomain
        fields = ['id','name','shortcode','size','cost_calculated_date','owner','days_extra_versions','days_only_version','versions_after_deleted','versions_while_exists','nodes']
        depth = 1


class VolumeInstanceSerializer(serializers.ModelSerializer):  # Base Serializer for Storage Volumes

    owner = serializers.StringRelatedField()
    service = serializers.StringRelatedField()
    rate = RateSerializer(read_only=True)


    def update(self, instance, validated_data):
        r = self.context['request']

        if 'option' in r.data:
            print(r.data['option'])
            try:
                instance.rate = StorageRate.objects.get(label=r.data['option'],service=instance.service,type=instance.type)
            except:
                print('error setting rate')

        if 'host_list' in r.data:
            instance.update_hosts(r.data['host_list'])

        return super().update(instance, validated_data)



class StorageInstanceSerializer(VolumeInstanceSerializer):

    class Meta:
        model = StorageInstance
        fields = ['id','name','owner','size','service','type','rate','shortcode','created_date','uid','ad_group','total_cost'
        ,'deptid','autogrow','flux']


class ArcBillingForInstanceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ArcBilling
        fields = ['size', 'shortcode']


class ArcInstanceSerializer(VolumeInstanceSerializer):
    hosts = serializers.StringRelatedField(many=True)
    shortcodes = ArcBillingForInstanceSerializer(many=True, read_only=True)
    prefetch_related = ['rate','shortcodes','hosts']
    select_related = ['owner','service']

    class Meta:
        model = ArcInstance
        fields = ['id','name','owner','size','service','type','rate','shortcodes', 'created_date','uid','ad_group','total_cost','hosts'
        ,'nfs_group_id','multi_protocol','sensitive_regulated','great_lakes','armis','lighthouse','globus','globus_phi','thunder_x','research_computing_package','college','amount_used']


class ArcBillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArcBilling
        fields = ['id', 'arc_instance', 'size', 'shortcode']

class NetworkSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    class Meta:
        fields = ['id','status','name','created_date','size','vlan_id','owner']
        model = Network

    def create(self, validated_data):
        instance = super().create(validated_data)    

        r = self.context['request']
        image = r.data.get('image')
        if image:
            i = Image.objects.get(name=image)
            i.network_id=instance.id
            i.save()

        return instance
class LDAPGroupMemberSerializer(serializers.ModelSerializer):
    ldap_group = serializers.StringRelatedField()

    class Meta:
        model = LDAPGroupMember
        fields = ['id', 'ldap_group', 'username']


class LDAPGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = LDAPGroup
        fields = ['id', 'name', 'active']
