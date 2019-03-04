from django.urls import path

from . import views

urlpatterns = [
    path('dept/<str:dept_id>', views.dept, name='dept'),
    path('user/<str:user_id>', views.user, name='user'),

    # Switch User
    path('su/', views.su_logout, name="su_logout"),
    path('su_login/', views.su_login, name="su_login"),
    path('?P<user_id>', views.login_as_user, name="login_as_user"),

]
