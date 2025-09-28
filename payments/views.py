from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Payment, PaymentMethod, PaymentTransaction, Refund

class PaymentListView(LoginRequiredMixin, ListView):
    """
    Payment list view
    """
    model = Payment
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return Payment.objects.all().order_by('-created_at')
        else:
            return Payment.objects.filter(order__customer=self.request.user).order_by('-created_at')


class PaymentDetailView(LoginRequiredMixin, DetailView):
    """
    Payment detail view
    """
    model = Payment
    template_name = 'payments/payment_detail.html'
    context_object_name = 'payment'


class PaymentCreateView(LoginRequiredMixin, CreateView):
    """
    Payment create view
    """
    model = Payment
    template_name = 'payments/payment_create.html'
    fields = ['payment_method', 'amount', 'payment_details']
    success_url = reverse_lazy('payments:payment_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'পেমেন্ট সফলভাবে তৈরি হয়েছে।')
        return response


class PaymentMethodListView(ListView):
    """
    Payment method list view
    """
    model = PaymentMethod
    template_name = 'payments/payment_method_list.html'
    context_object_name = 'payment_methods'
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(is_active=True).order_by('name')


class PaymentMethodDetailView(DetailView):
    """
    Payment method detail view
    """
    model = PaymentMethod
    template_name = 'payments/payment_method_detail.html'
    context_object_name = 'payment_method'


# Payment processing views
class BkashPaymentView(LoginRequiredMixin, TemplateView):
    """
    bKash payment view
    """
    template_name = 'payments/bkash_payment.html'


class NagadPaymentView(LoginRequiredMixin, TemplateView):
    """
    Nagad payment view
    """
    template_name = 'payments/nagad_payment.html'


class RocketPaymentView(LoginRequiredMixin, TemplateView):
    """
    Rocket payment view
    """
    template_name = 'payments/rocket_payment.html'


class BankTransferView(LoginRequiredMixin, TemplateView):
    """
    Bank transfer view
    """
    template_name = 'payments/bank_transfer.html'


class CardPaymentView(LoginRequiredMixin, TemplateView):
    """
    Card payment view
    """
    template_name = 'payments/card_payment.html'


# Payment callbacks
class BkashCallbackView(TemplateView):
    """
    bKash callback view
    """
    template_name = 'payments/bkash_callback.html'


class NagadCallbackView(TemplateView):
    """
    Nagad callback view
    """
    template_name = 'payments/nagad_callback.html'


class RocketCallbackView(TemplateView):
    """
    Rocket callback view
    """
    template_name = 'payments/rocket_callback.html'


# Payment processing
class PaymentProcessView(LoginRequiredMixin, TemplateView):
    """
    Payment process view
    """
    template_name = 'payments/payment_process.html'


class PaymentCompleteView(LoginRequiredMixin, TemplateView):
    """
    Payment complete view
    """
    template_name = 'payments/payment_complete.html'


class PaymentFailView(LoginRequiredMixin, TemplateView):
    """
    Payment fail view
    """
    template_name = 'payments/payment_fail.html'


# Refund views
class RefundListView(LoginRequiredMixin, ListView):
    """
    Refund list view
    """
    model = Refund
    template_name = 'payments/refund_list.html'
    context_object_name = 'refunds'
    paginate_by = 20
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return Refund.objects.all().order_by('-created_at')
        else:
            return Refund.objects.filter(payment__order__customer=self.request.user).order_by('-created_at')


class RefundDetailView(LoginRequiredMixin, DetailView):
    """
    Refund detail view
    """
    model = Refund
    template_name = 'payments/refund_detail.html'
    context_object_name = 'refund'


class RefundCreateView(LoginRequiredMixin, CreateView):
    """
    Refund create view
    """
    model = Refund
    template_name = 'payments/refund_create.html'
    fields = ['amount', 'reason']
    success_url = reverse_lazy('payments:refund_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'রিফান্ড অনুরোধ সফলভাবে জমা দেওয়া হয়েছে।')
        return response


class RefundProcessView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Refund process view (admin only)
    """
    template_name = 'payments/refund_process.html'
    
    def test_func(self):
        return self.request.user.is_admin


# Payment history
class PaymentHistoryView(LoginRequiredMixin, ListView):
    """
    Payment history view
    """
    model = Payment
    template_name = 'payments/payment_history.html'
    context_object_name = 'payments'
    paginate_by = 20
    
    def get_queryset(self):
        return Payment.objects.filter(order__customer=self.request.user).order_by('-created_at')


class PaymentHistoryDetailView(LoginRequiredMixin, DetailView):
    """
    Payment history detail view
    """
    model = Payment
    template_name = 'payments/payment_history_detail.html'
    context_object_name = 'payment'
    
    def get_queryset(self):
        return Payment.objects.filter(order__customer=self.request.user)


# Admin views
class AdminPaymentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Admin payment list view
    """
    model = Payment
    template_name = 'payments/admin_payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_admin
    
    def get_queryset(self):
        return Payment.objects.all().order_by('-created_at')


class AdminPaymentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Admin payment detail view
    """
    model = Payment
    template_name = 'payments/admin_payment_detail.html'
    context_object_name = 'payment'
    
    def test_func(self):
        return self.request.user.is_admin


class AdminRefundListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Admin refund list view
    """
    model = Refund
    template_name = 'payments/admin_refund_list.html'
    context_object_name = 'refunds'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_admin
    
    def get_queryset(self):
        return Refund.objects.all().order_by('-created_at')


class AdminRefundDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Admin refund detail view
    """
    model = Refund
    template_name = 'payments/admin_refund_detail.html'
    context_object_name = 'refund'
    
    def test_func(self):
        return self.request.user.is_admin


class AdminRefundApproveView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Admin refund approve view
    """
    template_name = 'payments/admin_refund_approve.html'
    
    def test_func(self):
        return self.request.user.is_admin


class AdminRefundRejectView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Admin refund reject view
    """
    template_name = 'payments/admin_refund_reject.html'
    
    def test_func(self):
        return self.request.user.is_admin