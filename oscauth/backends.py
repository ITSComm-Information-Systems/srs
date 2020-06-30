# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from project.pinnmodels import UmRteTechnicianV
from django.core.exceptions import PermissionDenied


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
        if perm == 'rte_access':
            return UmRteTechnicianV.objects.filter(uniqname=user_obj.username).exists()
            #     return True
            # else:
            #     raise PermissionDenied
        else:
            return True