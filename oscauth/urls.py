from django.urls import path

from . import views

urlpatterns = [
    path('dept/<str:dept_id>', views.dept, name='dept'),
    path('user/<str:user_id>', views.user, name='user'),

    # Switch User
    path('su/', views.su_logout, name="su_logout"),
    path('su_login/', views.su_login, name="su_login"),
    path('?P<user_id>', views.login_as_user, name="login_as_user"),
    path('adduser/', views.get_name),
    #path('ldap/user/', views.get_name),
    path('mypriv/', views.mypriv),
    path('get_dept/', views.get_dept),
    path('deptpriv/<str:dept_parm>/', views.deptpriv),
    path('deptpriv/', views.deptpriv),
    path('get_uniqname/', views.get_uniqname),
    path('setpriv/<str:uniqname_parm>/<str:last_name>/<str:first_name>/', views.setpriv),
    path('setpriv/<str:uniqname_parm>/', views.setpriv),
    path('setpriv/', views.setpriv),
    path('showpriv/<str:uniqname_parm>/<str:last_name>/<str:first_name>/', views.showpriv),
    path('showpriv/', views.showpriv),
    path('addpriv/<str:uniqname_parm>/<str:last_name>/<str:first_name>/', views.addpriv),
    path('addpriv/<str:uniqname_parm>/', views.addpriv),
    path('addpriv/', views.addpriv),
    path('removepriv/<str:uniqname_parm>/', views.removepriv),
    path('removepriv/', views.removepriv),

]
