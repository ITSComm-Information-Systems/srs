from django.urls import path
from . import views

urlpatterns = [
    path('single-tech/submitted/', views.single_submit),
    path('single-tech/get-assigned-group/', views.get_assigned_group),
    path('single-tech/', views.single_tech),
    path('multiple-tech/get-assigned-group/', views.get_assigned_group),
    path('multiple-tech/submitted/', views.multiple_submit),
    path('multiple-tech/', views.multiple_tech),
    path('update/submitted/', views.update_submit),
    path('update/get-update-entries/', views.get_update_entries),
    path('update/', views.update),
    path('view-time/display/', views.view_time_display),
    path('view-time/', views.view_time_load),
    path('actionlog/', views.get_action_log),
    path('actionlog/<int:id>/', views.get_action_log_entry),
    path('confirmation/', views.get_confirmation),
    path('actual-vs-estimate-open/', views.actual_v_estimate, name='actual-vs-estimate-open'),
    path('actual-vs-estimate-completed/', views.actual_v_estimate, name='actual-vs-estimate-completed'),
    path('employee-time-report/', views.employee_time_report, name='employee-time-report'),
    #path('estimate-mockup/', views.estimate_mockup, name='estimate-mockup'),
    path(r'', views.load_rte),
    
]
