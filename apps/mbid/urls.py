from django.urls import path
from . import views

app_name = 'mbid'
urlpatterns = [
    # Mike
    path('create_cycle/', views.create_cycle,name='create_cycle'),
    path('create_cycle/complete/<int:message>', views.complete),
    path('edit_cycle/', views.edit_cycle, name='edit_cycle'),
    path('review/', views.review, name='review'),
    path('review/complete/<int:message>', views.complete),

    # Vendor
    path('create_report/', views.create_cycle_report,name='create_report'),
    path('upload_bids/', views.upload_bids, name='upload_bids'),
    path('review_bids/',views.review_bids, name='review_bids'),

    # All
    path('faq/', views.faq, name='faq'),
    path(r'', views.home, name='home'), #keep at bottom

]
