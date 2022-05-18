from django.urls import path, re_path
from . import views

urlpatterns = [
    path('help', views.get_help),
    path('dept/<int:dept_id>/', views.StepSubscribers.as_view(), name='subscribers'),
    path('dept/<int:dept_id>/details/', views.StepDetails.as_view(), name='details'),
    path('dept/<int:dept_id>/confirmation/', views.StepConfirmation.as_view(), name='confirmation'),
    path('dept/<int:dept_id>/selections/', views.Selections.as_view(), name='selections'),
    re_path(r'^', views.landing_page)
]