from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('signup/delivery-agent/', views.DeliveryAgentSignupView.as_view(), name='delivery_agent_signup'),
    
    # Password management
    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password-change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    
    # Profile management
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('profile/delete/', views.ProfileDeleteView.as_view(), name='profile_delete'),
    
    # User dashboard
    path('dashboard/', views.UserDashboardView.as_view(), name='dashboard'),
    
    # Email verification
    path('verify-email/', views.EmailVerificationView.as_view(), name='email_verification'),
    path('verify-email/<str:token>/', views.EmailVerificationConfirmView.as_view(), name='email_verification_confirm'),
    
    # User management (admin only)
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', views.UserEditView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    
    # Delivery agent specific
    path('delivery-agents/', views.DeliveryAgentListView.as_view(), name='delivery_agent_list'),
    path('delivery-agents/<int:pk>/', views.DeliveryAgentDetailView.as_view(), name='delivery_agent_detail'),
    path('delivery-agents/<int:pk>/toggle-availability/', views.ToggleAvailabilityView.as_view(), name='toggle_availability'),
]
