from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group
from project.pinnmodels import UmCurrentDeptManagersV, UmOscDeptProfileV
from oscauth.utils import McGroup
from django.core.exceptions import ValidationError


class Role(models.Model):  
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)
    role = models.CharField(max_length=30,unique=True)
    role_description = models.CharField(max_length=1000)
    grantable_by_dept = models.BooleanField(default = False)
    active = models.BooleanField(default=True)
    inactivation_date = models.DateTimeField('Date Inactivated', blank=True, null=True)
    create_date = models.DateTimeField('Date Created', auto_now_add=True)
    created_by = models.CharField(max_length=150, default='Not implemented')
    last_update_date = models.DateTimeField('Last Date Updated', auto_now=True)
    last_updated_by = models.CharField(max_length=150, default='Not implemented')

    def __str__(self):
        return self.role

    def save(self, *args, **kwargs):
        if not self.active and self.inactivation_date is None:
            self.inactivation_date = timezone.now()
        elif self.active and self.inactivation_date is not None:
            self.inactivation_date = None
        if self.pk is None:
            self.created_by = 'Not implemented'
            self.last_updated_by = 'Not implemented'
        elif self.pk is not None:
            self.last_updated_by = 'Not implemented'
        super(Role, self).save(*args, **kwargs)

    class Meta:
        db_table = 'auth_role'
        permissions = [
            ('can_administer_access_all', 'Can Modify All Access Privileges'),
            ('can_administer_access', 'Can Modify Access Privileges (except proxy)'),
            ('can_order', 'All ordering functions'),
            ('can_report', 'Can run reports'),
            ('can_impersonate', 'Can Impersonate'),       
            ('can_move_voip', 'Can Submit VOIP Location Changes'),          
            ('can_report_all', 'Can run all reports without restrictions'), 
        ]


class DepartmentSecurityV(models.Model):
    username = models.CharField(max_length=150, blank=True, primary_key=True)             
    first_name = models.CharField(max_length=150, blank=True)           
    last_name = models.CharField(max_length=150, blank=True)           
    srs_role = models.CharField(max_length=150, blank=True)             
    deptid = models.CharField(max_length=10, blank=True)                
    dept_effdt = models.DateField()                                     
    dept_eff_status = models.CharField(max_length=1, blank=True)        
    dept_descr = models.CharField(max_length=30, blank=True)            
    emplid = models.CharField(max_length=11, blank=True)                
    dept_grp = models.CharField(max_length=20, blank=True)              
    dept_grp_descr = models.CharField(max_length=30, blank=True)        
    dept_grp_vp_area = models.CharField(max_length=20, blank=True)      
    dept_grp_vp_area_descr = models.CharField(max_length=30, blank=True)
    dept_grp_campus = models.CharField(max_length=20, blank=True)       
    dept_grp_campus_descr = models.CharField(max_length=30, blank=True) 
    dept_bud_seq = models.CharField(max_length=20, blank=True)          
    dept_bud_seq_descr = models.CharField(max_length=30, blank=True)    

    class Meta:
        managed = False
        db_table = 'department_security_v'
    

class AuthUserDeptV(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    codename = models.CharField(max_length=20, blank=True)
    dept = models.CharField(max_length=10, blank=True, primary_key=True)

    @property
    def dept_name(self):
        dept_name = UmOscDeptProfileV.objects.get(deptid=self.dept).dept_name
        return dept_name

    @property
    def dept_mgr(self):
        dept_mgr = UmOscDeptProfileV.objects.get(deptid=self.dept).dept_mgr
        return dept_mgr

    @property
    def dept_mgr_uniqname(self):
        dept_mgr_uniqname = UmOscDeptProfileV.objects.get(deptid=self.dept).dept_mgr_uniqname
        return dept_mgr_uniqname

    class Meta:
        managed = False
        db_table = 'auth_user_dept_v'

class AuthUserDept(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    dept = models.CharField(max_length=10, blank=True)

    class Meta:
        db_table = 'auth_user_dept'
        unique_together = (("user", "group", "dept"),)

    def get_order_departments(self):
        return AuthUserDeptV.objects.filter(user_id=self,codename='can_order')

    def get_report_departments(request):
        if request.user.has_perm('oscauth.can_report_all'):
            query = UmOscDeptProfileV.objects.filter(deptid__iregex=r'^[0-9]*$').order_by('deptid')
            return query
        else:
            query = AuthUserDeptV.objects.filter(user=request.user.id, codename='can_report').order_by('dept')
            full_depts = []
            for d in query:
                name = UmOscDeptProfileV.objects.filter(deptid=d.dept)[0].dept_name
                dept ={
                    'deptid': d.dept,
                    'dept_name': name
                }
                full_depts.append(dept)
            return full_depts


class Grantor(models.Model):
    grantor_role = models.ForeignKey(Group, on_delete=models.PROTECT)
    granted_role = models.ForeignKey(Role, on_delete=models.PROTECT)
    display_seq_no = models.PositiveIntegerField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.role

    class Meta:
        db_table = 'auth_grantor'
        unique_together = (("grantor_role", "granted_role"),)


class LDAPGroup(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def clean(self):
        mc = McGroup(self.name)  # Check name vs MCommunity

        if not hasattr(mc, 'dn'):
            raise ValidationError({'name': 'Group not found.'})
        else:
            self.id = mc.gidnumber

    def save(self, *args, **kwargs):
        if not self.pk:
            self.full_clean()  # Make sure the record exists in MCommunity

        super().save(*args, **kwargs)

    def lookup(self, name):
        mc = McGroup(name)  # Check name vs MCommunity

        if not hasattr(mc, 'dn'):
            return None

        try:
            lg = LDAPGroup.objects.get(name=mc.dn) # Lookup group with DN
            return lg
        except:
            lg = LDAPGroup()
            lg.name = mc.dn
            lg.id = mc.gidnumber
            lg.save()

            for member in mc.members:   # Add members since this is a new group
                lgm = LDAPGroupMember()
                lgm.ldap_group = lg
                lgm.username = member
                lgm.save()

            return lg

    def update_membership(self):
        mc = McGroup(self.name)

        #if not mc.dn:
        if not hasattr(mc, 'dn'):
            self.active = False
            self.save()
            return None
        
        if self.active == False:  # Reactivate group
            self.active = True
            self.save()

        db_members = set(LDAPGroupMember.objects.filter(ldap_group=self).values_list('username', flat=True) )

        for username in mc.members.difference(db_members):
            print('add', username)
            lgm = LDAPGroupMember()
            lgm.ldap_group = self
            lgm.username = username
            lgm.save()

        for username in db_members.difference(mc.members):
            LDAPGroupMember.objects.filter(ldap_group = self, username = username).delete()
            print('delete', username)

        return mc.members

    class Meta:
        ordering = ['name']


class LDAPGroupMember(models.Model):
    ldap_group = models.ForeignKey(LDAPGroup, on_delete=models.CASCADE)
    username = models.CharField(max_length=8)

    def __str__(self):
        return self.username