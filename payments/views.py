from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.http import JsonResponse
from decimal import Decimal
import json

from django.db.models import Sum
from .models import Payment, PaymentMethod, PaymentTransaction, Refund
from orders.models import Order, OrderStatusHistory


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return bool(user.is_authenticated and (
            user.is_staff or
            user.is_superuser or
            getattr(user, 'user_type', None) == 'admin'
        ))

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Administrative access required.')
            return redirect('dashboard:home')
        return super().handle_no_permission()


class PaymentListView(LoginRequiredMixin, ListView):
    """
    List payment transactions for the authenticated customer or admin.
    """
    model = Payment
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'user_type', None) == 'admin':
            queryset = Payment.objects.all().select_related('order', 'order__customer').order_by('-created_at')
        else:
            queryset = Payment.objects.filter(
                order__customer=user
            ).select_related('order').order_by('-created_at')

        method = self.request.GET.get('method')
        if method:
            queryset = queryset.filter(payment_method=method)

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = bool(self.request.user.is_staff or getattr(self.request.user, 'user_type', None) == 'admin')
        context['methods'] = Payment.PAYMENT_METHOD_CHOICES
        context['statuses'] = Payment.PAYMENT_STATUS_CHOICES
        context['selected_method'] = self.request.GET.get('method', '')
        context['selected_status'] = self.request.GET.get('status', '')
        return context


class PaymentDetailView(LoginRequiredMixin, DetailView):
    """
    Detailed transaction breakdown.
    """
    model = Payment
    template_name = 'payments/payment_detail.html'
    context_object_name = 'payment'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'user_type', None) == 'admin':
            return Payment.objects.all()
        return Payment.objects.filter(order__customer=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = self.object.transactions.order_by('-timestamp')
        context['refunds'] = self.object.refunds.order_by('-created_at')
        return context


class PaymentMethodListView(ListView):
    """
    Supported payment channels overview.
    """
    model = PaymentMethod
    template_name = 'payments/payment_method_list.html'
    context_object_name = 'payment_methods'

    def get_queryset(self):
        return PaymentMethod.objects.filter(is_active=True).order_by('id')


class AdminPaymentListView(AdminRequiredMixin, ListView):
    """
    Admin payments view with real financial totals.
    """
    model = Payment
    template_name = 'payments/admin_payment_list.html'
    context_object_name = 'payments'
    paginate_by = 25

    def get_queryset(self):
        queryset = Payment.objects.all().select_related('order', 'order__customer').order_by('-created_at')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        method = self.request.GET.get('method')
        if method:
            queryset = queryset.filter(payment_method=method)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_collected'] = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        context['pending_amount'] = Payment.objects.filter(status='pending').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        return context


# Import Sum from django.db.models
from django.db.models import Sum
