import warnings
import collections

from ldap3 import Server, Connection, ALL
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

def upsert_user(uniqname):
    # Get User from MCommunity.  Create them in OSC if they are not there otherwise update them.
    server = Server(settings.MCOMMUNITY['SERVER'], use_ssl=True, get_info=ALL)
    conn = Connection(server,
                      user=settings.MCOMMUNITY['USERNAME'],
                      password=settings.MCOMMUNITY['PASSWORD'],
                      auto_bind=True)

    conn.search('ou=People,dc=umich,dc=edu', '(uid=' + uniqname + ')', attributes=["uid","mail","user","givenName","umichDisplaySn"])
    
    if conn.entries:
        mc_user = conn.entries[0]
    else:
        return None
        
    try:
        osc_user = User.objects.get(username=uniqname)
    except:
        osc_user = User()

    osc_user.username = mc_user.uid
    osc_user.last_name = mc_user.umichDisplaySn
    osc_user.first_name = mc_user.givenName
    osc_user.email = mc_user.mail
    osc_user.save()

    return osc_user


def get_mc_user(uniqname):
    # Get User from MCommunity.  Create them in OSC if they are not there otherwise update them.
    server = Server(settings.MCOMMUNITY['SERVER'], use_ssl=True, get_info=ALL)
    conn = Connection(server,
                      user=settings.MCOMMUNITY['USERNAME'],
                      password=settings.MCOMMUNITY['PASSWORD'],
                      auto_bind=True)

    conn.search('ou=People,dc=umich,dc=edu', '(uid=' + uniqname + ')', attributes=["uid","mail","user","givenName","umichDisplaySn","telephoneNumber","umichInstRoles","displayName"])
    
    if conn.entries:
        return conn.entries[0] 
    else:
        return None


def get_mc_group(name):
    # Get User from MCommunity.  Create them in OSC if they are not there otherwise update them.
    server = Server(settings.MCOMMUNITY['SERVER'], use_ssl=True, get_info=ALL)
    conn = Connection(server,
                      user=settings.MCOMMUNITY['USERNAME'],
                      password=settings.MCOMMUNITY['PASSWORD'],
                      auto_bind=True)

    conn.search('ou=Groups,dc=umich,dc=edu', '(cn=' + name + ')', attributes=["member"])
    
    if conn.entries:
        #print(conn.entries)
        return conn.entries[0] 
    else:
        print(f'none found for {name}')
        return None

class McGroup:

    def __init__(self, name):
        server = Server(settings.MCOMMUNITY['SERVER'], use_ssl=True, get_info=ALL)
        conn = Connection(server,
                        user=settings.MCOMMUNITY['USERNAME'],
                        password=settings.MCOMMUNITY['PASSWORD'],
                        auto_bind=True)

        conn.search('ou=Groups,dc=umich,dc=edu', '(cn=' + name + ')', attributes=["member","gidnumber"])

        if conn.entries:
            self.response = conn.entries
            self.dn = conn.entries[0].entry_dn[3:conn.entries[0].entry_dn.find(',')]
            self.gidnumber = conn.entries[0].gidnumber.value

            self.members = set()

            for member in conn.entries[0]['member']:
                uid = member[4:member.find(',')]
                self.members.add(uid)  # Eliminate duplicates by adding to set

        else:
            print(f'none found for {name}')
            self = None
