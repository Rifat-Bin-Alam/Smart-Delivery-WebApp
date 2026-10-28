from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='payment_list'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('methods/', views.PaymentMethodListView.as_view(), name='payment_method_list'),
    path('admin/', views.AdminPaymentListView.as_view(), name='admin_payment_list'),
]
