from django.urls import path

from . import views

urlpatterns = [
    path('dept/<str:dept_id>', views.dept, name='dept'),
    path('user/<str:user_id>', views.user, name='user'),

    # Switch User
    path('su/', views.su_logout, name="su_logout"),
    path('su_login/', views.su_login, name="su_login"),
    path('logout/', views.logout_view),
    path('?P<user_id>', views.login_as_user, name="login_as_user"),
    path('adduser/', views.get_name),
    #path('ldap/user/', views.get_name),
    path('mypriv/', views.mypriv),
    path('showpriv/', views.showpriv),
    path('showpriv/<str:uniqname_parm>/', views.showpriv),
    path('get_dept/', views.get_dept),
    path('deptpriv/<str:dept_parm>/', views.deptpriv),
    path('deptpriv/', views.deptpriv),
    path('get_uniqname/', views.get_uniqname),
    path('modpriv/', views.modpriv),

    path('userid/',views.userid),

]
