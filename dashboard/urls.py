from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Landing page
    path('', views.HomeView.as_view(), name='home'),

    # Admin Dashboard & Inventory
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-panel/', views.AdminPanelView.as_view(), name='admin_panel'),

    # Customer Dashboard
    path('user-dashboard/', views.UserDashboardView.as_view(), name='user_dashboard'),

    # Support & Info
    path('faq/', views.FAQListView.as_view(), name='faq'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
]
