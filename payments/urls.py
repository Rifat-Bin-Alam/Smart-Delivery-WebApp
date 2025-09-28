from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment management
    path('', views.PaymentListView.as_view(), name='payment_list'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('create/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('<int:pk>/process/', views.PaymentProcessView.as_view(), name='payment_process'),
    path('<int:pk>/complete/', views.PaymentCompleteView.as_view(), name='payment_complete'),
    path('<int:pk>/fail/', views.PaymentFailView.as_view(), name='payment_fail'),
    
    # Payment methods
    path('methods/', views.PaymentMethodListView.as_view(), name='payment_method_list'),
    path('methods/<int:pk>/', views.PaymentMethodDetailView.as_view(), name='payment_method_detail'),
    
    # Payment processing
    path('bkash/', views.BkashPaymentView.as_view(), name='bkash_payment'),
    path('nagad/', views.NagadPaymentView.as_view(), name='nagad_payment'),
    path('rocket/', views.RocketPaymentView.as_view(), name='rocket_payment'),
    path('bank-transfer/', views.BankTransferView.as_view(), name='bank_transfer'),
    path('card/', views.CardPaymentView.as_view(), name='card_payment'),
    
    # Payment callbacks
    path('callback/bkash/', views.BkashCallbackView.as_view(), name='bkash_callback'),
    path('callback/nagad/', views.NagadCallbackView.as_view(), name='nagad_callback'),
    path('callback/rocket/', views.RocketCallbackView.as_view(), name='rocket_callback'),
    
    # Refunds
    path('refunds/', views.RefundListView.as_view(), name='refund_list'),
    path('refunds/<int:pk>/', views.RefundDetailView.as_view(), name='refund_detail'),
    path('refunds/create/', views.RefundCreateView.as_view(), name='refund_create'),
    path('refunds/<int:pk>/process/', views.RefundProcessView.as_view(), name='refund_process'),
    
    # Payment history
    path('history/', views.PaymentHistoryView.as_view(), name='payment_history'),
    path('history/<int:pk>/', views.PaymentHistoryDetailView.as_view(), name='payment_history_detail'),
    
    # Admin payment management
    path('admin/', views.AdminPaymentListView.as_view(), name='admin_payment_list'),
    path('admin/<int:pk>/', views.AdminPaymentDetailView.as_view(), name='admin_payment_detail'),
    path('admin/refunds/', views.AdminRefundListView.as_view(), name='admin_refund_list'),
    path('admin/refunds/<int:pk>/', views.AdminRefundDetailView.as_view(), name='admin_refund_detail'),
    path('admin/refunds/<int:pk>/approve/', views.AdminRefundApproveView.as_view(), name='admin_refund_approve'),
    path('admin/refunds/<int:pk>/reject/', views.AdminRefundRejectView.as_view(), name='admin_refund_reject'),
]
