# -*- coding: utf-8 -*-

import warnings
import collections
import ldap
from django.contrib.auth.models import User

from django.conf import settings

#from .compat import import_by_path as import_string


def su_login_callback(user):
    if hasattr(settings, 'SU_LOGIN'):
        warnings.warn(
            "SU_LOGIN is deprecated, use SU_LOGIN_CALLBACK",
            DeprecationWarning,
        )

    func = getattr(settings, 'SU_LOGIN_CALLBACK', None)
    if func is not None:
        if not isinstance(func, collections.Callable):
            func = import_string(func)
        return func(user)
    return user.has_perm('auth.change_user')


def custom_login_action(request, user):
    func = getattr(settings, 'SU_CUSTOM_LOGIN_ACTION', None)
    if func is None:
        return False

    if not isinstance(func, collections.Callable):
        func = import_string(func)
    func(request, user)

    return True

def get_ldap_user(username):

    print (username)
    searchFilter = 'uid=' + username    
    attributes = ["displayName","uid","mail","user","givenName","sn","telephoneNumber"]
    
    try: 
        l = ldap.initialize('ldap://ldap.umich.edu')
        basedn = "ou=People,dc=umich,dc=edu"

        l.protocol_version = ldap.VERSION3
        l.simple_bind_s() 
        print (searchFilter)
        ldap_result_id = l.search(basedn, ldap.SCOPE_SUBTREE, searchFilter, attributes)
        result_type, result_data = l.result(ldap_result_id, 0)

        return result_data
    
    except ldap.LDAPError as e:
        print (e)




class McUser(object):
    def __init__(self, uniqname):
        
        self.uniqname = uniqname
        
        self.name = ''
        self.email = ''
        self.phone = ''
        self.lastname = ''
        self.firstname = ''
        self.username = ''

        try:    
            result_data = get_ldap_user(uniqname)
        except:
            print ('Error')
            return

        try:
            self.name = result_data[0][1]['displayName'][0].decode()
            self.username = result_data[0][1]['uid'][0].decode()
            self.email = result_data[0][1]['mail'][0].decode()
            self.lastname = result_data[0][1]['sn'][0].decode()
            self.firstname = result_data[0][1]['givenName'][0].decode()
            self.phone = result_data[0][1]['telephoneNumber'][0].decode()
        except KeyError:
            print ('error: ' + uniqname)
            print (self.name)
            print (self.lastname)
            return

    def add_user(self):
        u = User()
        u.username = self.uniqname
        u.last_name = self.lastname
        u.first_name = self.firstname
        u.email = self.email
        u.save()