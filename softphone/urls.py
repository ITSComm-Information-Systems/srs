from django.urls import path, re_path
from . import views

urlpatterns = [
    path('help', views.get_help),
    path('pause/<str:uniqname>', views.PauseUser.as_view(), name='pause_user'),
    path('pause', views.PauseUser.as_view(), name='pause_user'),
    path('location', views.LocationChange.as_view(), name='location'),
    path('deskset/<int:dept_id>/', views.Deskset.as_view(), name='deskset'),
    path('dept/', views.department_selection, name='department_selection'),
    path('dept/<int:dept_id>/', views.StepSubscribers.as_view(), name='subscribers'),
    path('dept/<int:dept_id>/', views.StepSubscribers.as_view(), name='subscribers'),
    path('dept/<int:dept_id>/details/', views.StepDetails.as_view(), name='details'),
    path('dept/<int:dept_id>/confirmation/', views.StepConfirmation.as_view(), name='confirmation'),
    path('dept/<int:dept_id>/selections/', views.Selections.as_view(), name='selections'),
    path('dept/<int:dept_id>/selections/csv/', views.download_csv, name='selections'),
    re_path(r'^', views.landing_page)
]
