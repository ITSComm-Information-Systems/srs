from django.urls import path

from . import views

urlpatterns = [
    path('dept/<str:dept_id>', views.dept, name='dept'),
    path('user/<str:user_id>', views.user, name='user'),
]
