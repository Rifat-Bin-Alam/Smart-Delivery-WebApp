from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Products/Services (main page)
    path('', views.ProductListView.as_view(), name='product_list'),
    path('create/', views.OrderCreateView.as_view(), name='order_create'),
    
    # Cart and Checkout
    path('cart/', views.CartView.as_view(), name='cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('success/', views.OrderSuccessView.as_view(), name='order_success'),
    
    # Order management
    path('list/', views.OrderListView.as_view(), name='order_list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/edit/', views.OrderEditView.as_view(), name='order_edit'),
    path('<int:pk>/cancel/', views.OrderCancelView.as_view(), name='order_cancel'),
    path('<int:pk>/track/', views.OrderTrackView.as_view(), name='order_track'),
    path('invoice/<str:order_id>/', views.InvoiceView.as_view(), name='invoice'),
    
    # Order status management
    path('<int:pk>/status/', views.OrderStatusView.as_view(), name='order_status'),
    path('status/update/', views.OrderStatusUpdateView.as_view(), name='order_status_update'),
    
    # API endpoints
    path('api/admin/update-status/', views.admin_update_order_status, name='admin_update_order_status'),
    path('api/dashboard-data/', views.dashboard_data_api, name='dashboard_data_api'),
    path('api/create-order/', views.create_order_from_cart, name='create_order_from_cart'),
    
    # Products/Services
    path('products/', views.ProductListView.as_view(), name='products'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/category/<str:category>/', views.ProductCategoryView.as_view(), name='product_category'),
    
    # Order items
    path('<int:order_pk>/items/', views.OrderItemListView.as_view(), name='order_item_list'),
    path('<int:order_pk>/items/add/', views.OrderItemAddView.as_view(), name='order_item_add'),
    path('<int:order_pk>/items/<int:pk>/edit/', views.OrderItemEditView.as_view(), name='order_item_edit'),
    path('<int:order_pk>/items/<int:pk>/delete/', views.OrderItemDeleteView.as_view(), name='order_item_delete'),
    
    # Order history
    path('history/', views.OrderHistoryView.as_view(), name='order_history'),
    path('history/<int:pk>/', views.OrderHistoryDetailView.as_view(), name='order_history_detail'),
    
    # Admin order management
    path('admin/', views.AdminOrderListView.as_view(), name='admin_order_list'),
    path('admin/<int:pk>/', views.AdminOrderDetailView.as_view(), name='admin_order_detail'),
    path('admin/<int:pk>/assign/', views.AssignDeliveryAgentView.as_view(), name='assign_delivery_agent'),
    path('admin/<int:pk>/status/update/', views.AdminOrderStatusUpdateView.as_view(), name='admin_order_status_update'),
    
    # API endpoints
    path('api/create-order/', views.create_order_from_cart, name='create_order_api'),
    path('api/add-product/', views.add_product, name='add_product_api'),
    path('api/update-product/<int:product_id>/', views.update_product, name='update_product_api'),
    path('api/delete-product/<int:product_id>/', views.delete_product, name='delete_product_api'),
]
