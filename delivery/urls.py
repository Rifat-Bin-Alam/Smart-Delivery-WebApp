from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    # Delivery Partner Workspace
    path('', views.MyDeliveriesView.as_view(), name='my_deliveries'),
    path('my-deliveries/', views.MyDeliveriesView.as_view(), name='my_deliveries_alias'),
    path('my-deliveries/<int:pk>/', views.MyDeliveryDetailView.as_view(), name='my_delivery_detail'),
    path('<int:pk>/update-status/', views.DeliveryStatusUpdateView.as_view(), name='delivery_status_update'),
    path('location/update/', views.LocationUpdateView.as_view(), name='location_update'),

    # Coverage Areas
    path('areas/', views.DeliveryAreaListView.as_view(), name='delivery_area_list'),

    # Ratings
    path('<int:pk>/rate/', views.DeliveryRateView.as_view(), name='delivery_rate'),

    # Administrative Delivery Controls
    path('admin/', views.AdminDeliveryListView.as_view(), name='admin_delivery_list'),
    path('admin/agents/', views.AdminDeliveryAgentListView.as_view(), name='admin_delivery_agent_list'),
]
