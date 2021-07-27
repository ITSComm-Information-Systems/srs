from rest_framework import serializers

from project.models import Choice
from order.models import StorageInstance, ArcInstance, StorageRate, BackupDomain, BackupNode, ArcBilling, BackupDomain, Server, Database, ServerDisk
from oscauth.models import LDAPGroup, LDAPGroupMember
from django.db import models

class ServerDiskSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServerDisk
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

    for fld in model._meta.get_fields():
        if type(fld) == models.fields.related.ForeignKey:
            if fld.related_model == Choice:
                class_attrs[fld.name] = ChoiceSerializer()
            else:
                class_attrs[fld.name] = serializers.StringRelatedField()
        elif type(fld) == models.fields.related.ManyToManyField:
            if fld.related_model == Choice:
                class_attrs[fld.name] = ChoiceSerializer(many=True)
            else:
                class_attrs[fld.name] = serializers.StringRelatedField(many=True)

    if model == Server:   #TODO handle children
        class_attrs['disks'] = ServerDiskSerializer(many=True, read_only=True)


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


class BackupDomainSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    nodes = serializers.StringRelatedField(many=True)

    class Meta:
        model = BackupDomain
        fields = ['id','name','shortcode','size','cost_calculated_date','owner','days_extra_versions','days_only_version','versions_after_deleted','versions_while_exists','nodes']


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

    class Meta:
        model = ArcInstance
        fields = ['id','name','owner','size','service','type','rate','shortcodes', 'created_date','uid','ad_group','total_cost','hosts'
        ,'nfs_group_id','multi_protocol','sensitive_regulated','great_lakes','armis','lighthouse','globus','globus_phi','thunder_x','research_computing_package']


class ArcBillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArcBilling
        fields = ['id', 'arc_instance', 'size', 'shortcode']


class LDAPGroupMemberSerializer(serializers.ModelSerializer):
    ldap_group = serializers.StringRelatedField()

    class Meta:
        model = LDAPGroupMember
        fields = ['id', 'ldap_group', 'username']


class LDAPGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = LDAPGroup
        fields = ['id', 'name', 'active']
