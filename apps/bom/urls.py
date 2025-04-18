from django.urls import path
from django.views.generic import TemplateView

from . import views, reports

urlpatterns = [
    path('', TemplateView.as_view(template_name="bom/home.html")),
    path('favorites/', views.Favorites.as_view()),
    path('search/', views.Search.as_view()),
    path('search_ajax/', views.search_ajax),
    path('create_estimate/', views.create_estimate),
    path('add_new_part/', views.add_new_part),
    path('edit_material_location/', views.edit_material_location),
    path('edit_project/', views.edit_project),
    path('upload_csv/', views.upload_csv),
    path('item_lookup/', views.item_lookup),
    path('item-lookup-endpoint/', views.item_lookup_endpoint, name='item_lookup_endpoint'),
    path('items/<int:item_pk>/usage-count/', views.item_usage_count, name='item_usage_count'),
    path('notify_warehouse/', views.notify_warehouse),
    path('add_pinnacle_note/', views.add_pinnacle_note),
    path('add_item/<int:estimate_id>/', views.AddItem.as_view()),
    path('estimate/<int:estimate_id>/', views.Estimates.as_view(), name='estimate'),
    path('warehouse/<int:estimate_id>/', views.Warehouse.as_view()),
    path('by-location-report/<int:estimate_id>', reports.by_location_report),
    path('checkout-list-report/<int:estimate_id>', reports.checkout_list_report),
    path('summary-report/<int:estimate_id>', reports.summary_report),
    path('netops/', views.NetOpsSearch.as_view()),
    path('engineering/', views.EngineeringSearch.as_view()),
    path('estimate_search/', views.estimate_search, name='estimate_search'),
    path('estimate_search_endpoint/', views.estimate_search_endpoint, name='estimate_search_endpoint'),
    path('open_preorder_search/', views.open_preorder_search, name='open_preorder_search'),
    path('open_preorder_endpoint/', views.open_preorder_endpoint, name='open_preorder_endpoint'),
]
