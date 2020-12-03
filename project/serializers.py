from rest_framework import serializers

from order.models import StorageInstance, ArcInstance, StorageRate, BackupDomain, BackupNode, ArcBilling, BackupDomain
from oscauth.models import LDAPGroup, LDAPGroupMember


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

        try:   # If an option is passed look up by label and update rate
            request = self.context['request']
            instance.rate = StorageRate.objects.get(label=request.POST['option'],service=instance.service,type=instance.type)
        except:
            pass

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
        ,'nfs_group_id','multi_protocol','sensitive_regulated','great_lakes','armis','lighthouse','globus','globus_phi','thunder_x']


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