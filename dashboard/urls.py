from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Home page
    path('', views.HomeView.as_view(), name='home'),
    
    # Test page
    path('test/', views.TestView.as_view(), name='test'),
    
    # Database viewer
    path('database-viewer/', views.DatabaseViewerView.as_view(), name='database_viewer'),
    
    # Notifications
    path('notifications/stream/', views.NotificationStreamView.as_view(), name='notification_stream'),
    
    # Admin dashboard
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-panel/', views.AdminPanelView.as_view(), name='admin_panel'),
    
    # User dashboard
    path('user-dashboard/', views.UserDashboardView.as_view(), name='user_dashboard'),
    
    # Analytics
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    
    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', views.MarkNotificationReadView.as_view(), name='mark_notification_read'),
    
    # FAQ
    path('faq/', views.FAQListView.as_view(), name='faq'),
    
    # Contact
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # Reports
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('reports/orders/', views.OrderReportView.as_view(), name='order_report'),
    path('reports/revenue/', views.RevenueReportView.as_view(), name='revenue_report'),
    path('reports/delivery/', views.DeliveryReportView.as_view(), name='delivery_report'),
]
