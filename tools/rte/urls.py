from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('single-tech/', views.single_tech),
    # path('multiple-tech/', views.multiple_tech),
    # path('update/', views.update),
    url(r'', views.load_rte),
    
]
