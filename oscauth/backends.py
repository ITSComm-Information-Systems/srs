# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from project.pinnmodels import UmRteTechnicianV


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


class RTEBackend(BaseBackend):
    def has_perm(self, user_obj, perm, obj=None):
        return UmRteTechnicianV.objects.filter(uniqname=user_obj.username).exists()