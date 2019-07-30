from django.urls import path

from . import views

urlpatterns = [
	path('select-cf/', views.select_cf),
	path('report/<str:type>/detail/restart', views.restart),
	path('report/<str:type>/detail/', views.show_detail),
	path('report/<str:type>/', views.generate_report),
    path('', views.get_doc, name='base_doc'),
    
]
