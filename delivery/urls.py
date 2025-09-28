from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    # Delivery management
    path('', views.DeliveryListView.as_view(), name='delivery_list'),
    path('<int:pk>/', views.DeliveryDetailView.as_view(), name='delivery_detail'),
    path('<int:pk>/update-status/', views.DeliveryStatusUpdateView.as_view(), name='delivery_status_update'),
    path('<int:pk>/complete/', views.DeliveryCompleteView.as_view(), name='delivery_complete'),
    
    # Delivery agent specific
    path('my-deliveries/', views.MyDeliveriesView.as_view(), name='my_deliveries'),
    path('my-deliveries/<int:pk>/', views.MyDeliveryDetailView.as_view(), name='my_delivery_detail'),
    path('my-deliveries/<int:pk>/pickup/', views.DeliveryPickupView.as_view(), name='delivery_pickup'),
    path('my-deliveries/<int:pk>/deliver/', views.DeliveryDeliverView.as_view(), name='delivery_deliver'),
    
    # Location tracking
    path('location/update/', views.LocationUpdateView.as_view(), name='location_update'),
    path('location/history/', views.LocationHistoryView.as_view(), name='location_history'),
    
    # Delivery areas
    path('areas/', views.DeliveryAreaListView.as_view(), name='delivery_area_list'),
    path('areas/<int:pk>/', views.DeliveryAreaDetailView.as_view(), name='delivery_area_detail'),
    
    # Delivery ratings
    path('<int:pk>/rate/', views.DeliveryRateView.as_view(), name='delivery_rate'),
    path('ratings/', views.DeliveryRatingListView.as_view(), name='delivery_rating_list'),
    
    # Admin delivery management
    path('admin/', views.AdminDeliveryListView.as_view(), name='admin_delivery_list'),
    path('admin/assign/', views.AdminDeliveryAssignView.as_view(), name='admin_delivery_assign'),
    path('admin/agents/', views.AdminDeliveryAgentListView.as_view(), name='admin_delivery_agent_list'),
    path('admin/agents/<int:pk>/', views.AdminDeliveryAgentDetailView.as_view(), name='admin_delivery_agent_detail'),
    path('admin/agents/<int:pk>/assign/', views.AdminAssignDeliveryView.as_view(), name='admin_assign_delivery'),
]
