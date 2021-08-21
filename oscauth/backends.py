# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from project.pinnmodels import UmRteTechnicianV, UmBomProcurementUsersV


class SuBackend(object):
    supports_inactive_user = False

    def authenticate(self, request=None, su=False, user_id=None, **kwargs):
        if not su:
            return None

        try:
            user = get_user_model()._default_manager.get(
                pk=user_id)  # pylint: disable=W0212
        except (get_user_model().DoesNotExist, ValueError):
            return None

        return user

    def get_user(self, user_id):
        try:
            return get_user_model()._default_manager.get(
                pk=user_id)  # pylint: disable=W0212
        except get_user_model().DoesNotExist:
            return None

    def has_perm(self, user_obj, perm, obj=None):
        if perm == 'bom.can_access_bom':
            return UmRteTechnicianV.objects.filter(uniqname=user_obj.username).exists()
        elif perm == 'bom.can_update_bom_ordered':
            return UmBomProcurementUsersV.objects.filter(username=user_obj.username.upper(), security_role_code='UM Procurement').exists()
        elif perm == 'rte.add_umrteinput':
            return UmRteTechnicianV.objects.filter(uniqname=user_obj.username).exists()

        elif perm == 'mbid_procurement':
            return UmBomProcurementUsersV.objects.filter(username=user_obj.username.upper(), security_role_code='UM Procurement').exists()
        elif perm == 'is_vendor':
            return UmEcommMbidVendorV.objects.filter(email_address=user_obj.email).exists()
        else:
            return None

